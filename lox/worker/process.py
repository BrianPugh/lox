"""
.. module:: process
   :synopsis: Easily execute a function in multiple processes.

Calling the decorated function as normal will put it on a queue

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


import pathos.multiprocessing as mp
from .worker import WorkerWrapper
from collections import deque

__all__ = ['process',]

class _ProcessWrapper(WorkerWrapper):
    """Process helper decorator
    """

    def __init__(self, n_workers, func):
        super().__init__(n_workers, func)
        self.pool = mp.Pool(n_workers)

    def __len__(self):
        """ Returns the number of jobs not yet completed
        """

        count = 0
        for res in self.response:
            if not res.ready():
                count += 1

        return count

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary
        """
        self.response.append(self.pool.apply_async(self.func, args=args, kwds=kwargs))

    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other processes.
        Returns list of results in order scatter'd
        """
        fetched = [x.get() for x in self.response]
        self.response = deque()
        return fetched

def process(n_workers):
    """ Decorator to execute a function in multiple processes

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

    Methods
    -------
    __call__( \*args, \*\*kwargs )
        Vanilla passthrough function execution. Default user function behavior.

    __len__()
        Returns the current job queue length

    scatter( \*args, \*\*kwargs)
        Start a job executing func( \*args, \*\*kwargs ).
        Workers are spun up automatically.
        Obtain results via gather()

    gather()
        Block until all jobs called via scatter() are complete.
        Returns a list of results in the order that scatter was invoked.

    Parameters
    ----------
    n_workers : int
        Number of process workers to invoke. Defaults to number of CPU cores.
    """

    def wrapper(func):
        return _ProcessWrapper(n_workers, func)

    if isinstance(n_workers, int):
        # assume this is being called from decorator like "lox.process(5)"
        return wrapper
    else:
        # assume decorator with called as "lox.process"
        func = n_workers
        n_workers = mp.cpu_count()
        return _ProcessWrapper(n_workers, func)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
