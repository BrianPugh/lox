"""
.. module:: thread
   :synopsis: Easily execute a function or method in multiple threads.

Still allows the decorated function/method as normal.

Example:

.. doctest::

    >>> import lox
    >>> 
    >>> @lox.thread(4) # Will operate with a maximum of 4 threads
    ... def foo(x,y):
    ...     return x*y
    >>> foo(3,4)
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i+1)
    -ignore-
    >>> # foo is currently being executed in 4 threads
    >>> results = foo.gather() # block until results are ready
    >>> print(results) # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]
"""

from collections import namedtuple, deque
from threading import Lock, BoundedSemaphore
from time import time, sleep
import concurrent.futures
import functools
import logging as log
import queue
import sys
import threading
import traceback
from ..lock import LightSwitch
from ..helper import auto_adapt_to_methods, MethodDecoratorAdaptor, term_colors
from ..queue import Announcement
#from .worker import WorkerWrapper, ScatterPromise

__all__ = ["thread", ]

class ScatterGatherCallable:
    def __init__(self, fn, instance, executor, pending, pending_lock):
        self._fn = fn
        self._instance = instance
        self._executor = executor
        self._pending = pending
        self._pending_lock = pending_lock

    def __call__(self, *args, **kwargs):
        if self._instance is not None:
            args = (self._instance,) + args
        return self._fn(*args, **kwargs)

    def scatter(self, *args, **kwargs):
        if self._instance is not None:
            args = (self._instance,) + args
        with self._pending_lock:
            fut = self._executor.submit(self._fn, *args, **kwargs)
            self._pending.append(fut)
        return fut

    def gather(self):
        pending = []
        with self._pending_lock:
            pending[:] = self._pending
            self._pending[:] = []
        return [fut.result() for fut in pending]

class ScatterGatherDescriptor:
    def __init__(self, fn, worker_n):
        self._fn = fn
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=worker_n)
        self._pending = []
        self._pending_lock = threading.Lock()
        self._base_callable = ScatterGatherCallable(self._fn, None, self._executor, self._pending, self._pending_lock)

    def __call__(self, *args, **kwargs):
        """
        Vanilla passthrough function execution. Default user function behavior.

        Returns
        -------
        Decorated function return type.
           Return of decorated function.
        """

        return self._fn(*args, **kwargs)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return ScatterGatherCallable(self._fn, instance, self._executor, self._pending, self._pending_lock)

    def __len__(self):
        """ 
        Returns
        -------
            Approximate length of unprocessed job queue.
        """

        return self._executor._work_queue.qsize()

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary.

        Return
        ------
        concurrent.futures.Future
        """

        return self._base_callable.scatter(*args, **kwargs)

    def gather(self):
        """ Block and collect results from prior ``scatter`` calls.
        """

        return self._base_callable.gather()

def thread(worker_n):
    """ Decorator to execute a function in multiple threads.

    Example:

    .. doctest::

        >>> import lox
        >>> 
        >>> @lox.thread(4) # Will operate with a maximum of 4 threads
        ... def foo(x,y):
        ...     return x*y
        >>> foo(3,4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i+1)
        -ignore-
        >>> # foo is currently being executed in 4 threads
        >>> results = foo.gather()
        >>> print(results)
        [0, 2, 6, 12, 20]

    Multiple decorated functions can be chained together, each function drawing
    from their own pool of threads. Functions that return tuples will automatically
    unpack into the chained function. Positional arguments and keyword arguments
    can be passed in as they normally would.

    .. doctest::
        >>> @lox.thread(2) # Will operate with a maximum of 2 threads
        ... def bar(x,y):
        ...     return x + y

        >>>  for i in range(5):
        ...    foo_res = foo.scatter(i, i+1)
        ...    bar.scatter(foo_res, 10) # scatter will automatically unpack the results of foo 
        >>>  
        >>> results = bar.gather() 

    Parameters
    ----------
    max_workers : int
        Maximum number of threads to invoke.
        When ``lox.thread`` is called without ``()``, the wrapped function 
        a default number of max_workers is used (50).

    Methods
    -------
    __call__( *args, **kwargs )
        Vanilla passthrough function execution. Default user function behavior.

        Returns
        -------
        Decorated function return type.
           Return of decorated function.

    __len__()
        Returns
        -------
        int
            Current job queue length. Number of jobs that are currently waiting
            for an available worker.

    scatter( *args, **kwargs)
        Start a job executing decorated function ``func( *args, **kwargs )``.
        Workers are created and destroyed automatically.

    gather()
        Block until all jobs called via ``scatter()`` are complete.

        Returns
        -------
        list
            Results in the order that scatter was invoked.
    """

    # Support @thread with no arguments.
    if callable(worker_n):
        return thread(50)(worker_n)

    def decorator(fn):
        return ScatterGatherDescriptor(fn, worker_n)

    return decorator


if __name__ == '__main__':
    import doctest
    doctest.testmod()
