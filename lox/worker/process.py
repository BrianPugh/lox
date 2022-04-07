"""
.. module:: process
   :synopsis: Easily execute a function or method in multiple processes.

Still allows the decorated function/method as normal.

Example
-------
    .. doctest::
        :skipif: True

        >>> import lox
        >>>
        >>> @lox.process(4)  # Will operate with a maximum of 4 processes
        ... def foo(x, y):
        ...     return x * y
        ...
        >>> foo(3, 4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i + 1)
        ...
        >>> # foo is currently being executed in 4 processes
        >>> results = foo.gather()
        >>> print(results)
        [0, 2, 6, 12, 20]
"""


import os
import threading
from collections import deque

import pathos.multiprocessing as mp

from ..debug import LOX_DEBUG

try:
    from tqdm import tqdm as TQDM  # to avoid argument namespace collisions.
except ModuleNotFoundError:
    TQDM = None


__all__ = [
    "process",
]


class ScatterGatherCallable:
    def __init__(self, fn, instance, executor, pending, n_workers):
        self._fn = fn
        self._instance = instance
        self._executor = executor
        self._pending = pending
        self._n_workers = n_workers
        self._results_thread_lock = threading.Lock()
        self._tqdm = None
        self._tqdm_pre_update = 0  # Stores updates before we have a tqdm object.

    def __call__(self, *args, **kwargs):
        if self._instance is not None:
            args = (self._instance,) + args
        return self._fn(*args, **kwargs)

    def scatter(self, *args, **kwargs):
        if self._instance is not None:
            args = (self._instance,) + args

        if self._executor[0] is None:
            # We create the pool here for greater serialization compatability
            self._executor[0] = mp.Pool(self._n_workers)

        def callback(res):
            # All of these are executed in a single "results" thread
            with self._results_thread_lock:
                if self._tqdm is not None:
                    self._tqdm.update(1)
                else:
                    self._tqdm_pre_update += 1

        fut = self._executor[0].apply_async(
            self._fn, args=args, kwds=kwargs, callback=callback
        )
        self._pending.append(fut)

        return fut

    def gather(self, *, tqdm=None):
        if tqdm is not None:
            if TQDM is None:
                raise ModuleNotFoundError("No module named 'tqdm'")

            if isinstance(tqdm, bool) and tqdm:
                tqdm = TQDM(total=len(self._pending))

            with self._results_thread_lock:
                self._tqdm = tqdm
                # Update the progressbar with all of the results from before
                # the TQDM object was declared.
                self._tqdm.update(self._tqdm_pre_update)

        self._executor[0].close()
        self._executor[0].join()
        fetched = [x.get() for x in self._pending]
        self._pending.clear()
        self._executor[0] = None
        return fetched


class ScatterGatherDescriptor:
    def __init__(self, fn, n_workers):
        self._executor = [None]  # Make a list to share a "pointer"
        self._n_workers = n_workers
        self._fn = fn
        self._pending = deque()
        self._base_callable = ScatterGatherCallable(
            self._fn, None, self._executor, self._pending, self._n_workers
        )

    def __call__(self, *args, **kwargs):
        """
        Vanilla passthrough function execution. Default user function behavior.

        Returns
        -------
        Decorated function return type.
           Return of decorated function.
        """

        return self._fn(*args, **kwargs)

    def __len__(self):
        """Return length of unprocessed job queue.

        Returns
        -------
            Approximate length of unprocessed job queue.
        """

        count = 0
        for res in self._pending:
            if not res.ready():
                count += 1

        return count

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return ScatterGatherCallable(
            self._fn, instance, self._executor, self._pending, self._n_workers
        )

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary.

        Return
        ------
        concurrent.futures.Future
        """

        return self._base_callable.scatter(*args, **kwargs)

    def gather(self, *args, **kwargs):
        """Block and collect results from prior ``scatter`` calls."""

        results = self._base_callable.gather(*args, **kwargs)
        self._executor = None
        return results


def process(n_workers):
    """Decorate a function/method to execute in multiple processes.

    Example
    -------
    .. doctest::
        :skipif: True

        >>> import lox
        >>>
        >>> @lox.process(4)  # Will operate with a maximum of 4 processes
        ... def foo(x, y):
        ...     return x * y
        ...
        >>> foo(3, 4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i + 1)
        ...
        >>> # foo is currently being executed in 4 processes
        >>> results = foo.gather()
        >>> print(results)
        [0, 2, 6, 12, 20]

    Parameters
    ----------
    n_workers : int
        Number of process workers to invoke. Defaults to number of CPU cores.

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
            job queue length.
    scatter( *args, **kwargs )
        Start a job executing ``func( *args, **kwargs )``.
        Workers are created and destroyed automatically.

        Returns
        -------
        int
            Solution's index into the results obtained via ``gather()``.
    gather()
        Block until all jobs called via ``scatter()`` are complete.

        Returns
        -------
        list
            Results in the order that scatter was invoked.
    """  # noqa: D214,D215,D410,D411

    # Support @process with no arguments.
    if callable(n_workers):
        return process(os.cpu_count())(n_workers)

    def decorator(fn):
        return ScatterGatherDescriptor(fn, 0 if LOX_DEBUG else n_workers)

    return decorator


if __name__ == "__main__":
    import doctest

    doctest.testmod()
