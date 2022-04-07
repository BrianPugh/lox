"""
.. module:: thread
   :synopsis: Easily execute a function or method in multiple threads.

Still allows the decorated function/method as normal.

Example
-------
.. doctest::

    >>> import lox
    >>>
    >>> @lox.thread(4)  # Will operate with a maximum of 4 threads
    ... def foo(x, y):
    ...     return x * y
    ...
    >>> foo(3, 4)
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i + 1)
    ...
    -ignore-
    >>> # foo is currently being executed in 4 threads
    >>> results = foo.gather()  # block until results are ready
    >>> print(results)  # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]
"""

import concurrent.futures
import threading

from ..debug import LOX_DEBUG

try:
    from tqdm import tqdm as TQDM  # to avoid argument namespace collisions.
except ModuleNotFoundError:
    TQDM = None


__all__ = [
    "thread",
]


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
            if self._executor:
                fut = self._executor.submit(self._fn, *args, **kwargs)
            else:
                # Execute function in current thread
                fut = concurrent.futures.Future()
                fut.set_running_or_notify_cancel()
                try:
                    res = self._fn(*args, **kwargs)
                except Exception as e:
                    fut.set_exception(e)
                else:
                    fut.set_result(res)
            self._pending.append(fut)
        return fut

    def gather(self, *, tqdm=None):
        """
        Parameters
        ----------
        tqdm : tqdm.tqdm or bool
            If ``True``, will internally create and update a default tqdm object.
            If ``tqdm``, initialized tqdm object to update with progress.
        """

        pending = []
        with self._pending_lock:
            pending[:] = self._pending
            self._pending[:] = []

        if tqdm is not None:
            if TQDM is None:
                raise ModuleNotFoundError("No module named 'tqdm'")

            if isinstance(tqdm, bool) and tqdm:
                tqdm = TQDM(total=len(pending))

            # We need a mutex for the tqdm object since multiple callbacks
            # can be called at the same time via different threads under
            # the same parent process.
            tqdm_mutex = threading.Lock()

            def tqdm_callback(fut):
                with tqdm_mutex:
                    tqdm.update(1)

            [fut.add_done_callback(tqdm_callback) for fut in pending]

        output = [fut.result() for fut in pending]

        return output


class ScatterGatherDescriptor:
    def __init__(self, fn, n_workers):
        """
        Note: define self._executor in child class before calling this
        """

        self._pending_lock = threading.Lock()
        self._fn = fn
        self._pending = []

        if n_workers:
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=n_workers
            )
        else:
            # Disable threading; scatter calls are blocking; useful
            # for debugging multithreaded functions.
            self._executor = None

        self._base_callable = ScatterGatherCallable(
            self._fn, None, self._executor, self._pending, self._pending_lock
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

        if self._executor:
            return self._executor._work_queue.qsize()
        else:
            return 0

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return ScatterGatherCallable(
            self._fn, instance, self._executor, self._pending, self._pending_lock
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

        return self._base_callable.gather(*args, **kwargs)


def thread(n_workers):
    """Decorate a function/method to execute in multiple threads.

    Example:

    .. doctest::

        >>> import lox
        >>>
        >>> @lox.thread(4)  # Will operate with a maximum of 4 threads
        ... def foo(x, y):
        ...     return x * y
        ...
        >>> foo(3, 4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i + 1)
        ...
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
        >>> @lox.thread(2)  # Will operate with a maximum of 2 threads
        ... def bar(x, y):
        ...     return x + y
        ...

        >>> for i in range(5):
        ...     foo_res = foo.scatter(i, i + 1)
        ...     bar.scatter(foo_res, 10)  # scatter will automatically
        ...     # unpack the results of foo
        ...
        >>>
        >>> results = bar.gather()

    Parameters
    ----------
    max_workers : int
        Maximum number of threads to invoke.
        When ``lox.thread`` is called without ``()``, the wrapped function
        a default number of max_workers is used (50).
        If set to 0, scatter calls will be executed in the parent thread.

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
    """  # noqa: D214,D215,D410,D411

    # Support @thread with no arguments.
    if callable(n_workers):
        return thread(50)(n_workers)

    def decorator(fn):
        return ScatterGatherDescriptor(fn, 0 if LOX_DEBUG else n_workers)

    return decorator


if __name__ == "__main__":
    import doctest

    doctest.testmod()
