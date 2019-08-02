"""
.. module:: process
   :synopsis: Easily execute a function or method in multiple processes.

Still allows the decorated function/method as normal.

Example:

    .. doctest::
        :skipif: True

        >>> import lox
        >>> 
        >>> @lox.process(4) # Will operate with a maximum of 4 processes
        ... def foo(x,y):
        ...     return x*y
        >>> foo(3,4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i+1)
        >>> # foo is currently being executed in 4 processes
        >>> results = foo.gather()
        >>> print(results)
        [0, 2, 6, 12, 20]

"""


from collections import deque
import pathos.multiprocessing as mp
import logging as log
import sys
from .worker import WorkerWrapper
from ..helper import auto_adapt_to_methods, MethodDecoratorAdaptor

__all__ = ['process',]

class _ProcessWrapper(WorkerWrapper):
    """Process helper decorator.
    """

    def __init__(self, func, n_workers=None):
        if n_workers is None:
            n_workers = mp.cpu_count()
        super().__init__(n_workers, func)
        self.pool = None

    def __len__(self):
        """ 
        Returns
        -------
        int
            Number of jobs not yet completed.
        """

        count = 0
        for res in self.response:
            if not res.ready():
                count += 1

        return count

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary.

        Returns
        -------
        int
            Index into solution list.
        """
        if self.pool is None:
            self.pool = mp.Pool(self.n_workers,)
        self.response.append(self.pool.apply_async(self.func, args=args, kwds=kwargs))
        return len(self.response)-1

    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other processes.

        Returns
        -------
        list
            Results in order scatter'd
        """

        self.pool.close()
        self.pool.join()
        del self.pool
        fetched = [x.get() for x in self.response]
        self.response = deque()
        self.pool = None
        return fetched

def process(n_workers):
    """ Decorator to execute a function/method in multiple processes.

    Example:

    .. doctest::
        :skipif: True

        >>> import lox
        >>> 
        >>> @lox.process(4) # Will operate with a maximum of 4 processes
        ... def foo(x,y):
        ...     return x*y
        >>> foo(3,4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i+1)
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
    """

    @auto_adapt_to_methods
    def wrapper(func):
        return _ProcessWrapper(func, n_workers=n_workers)

    if isinstance(n_workers, int):
        # assume this is being called from decorator like "lox.process(5)"
        return wrapper
    else:
        # assume decorator with called as "lox.process"
        func = n_workers
        return MethodDecoratorAdaptor(_ProcessWrapper, func)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
