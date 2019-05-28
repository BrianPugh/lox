"""
.. module:: process
   :synopsis: Easily execute a function in multiple processes.

Calling the decorated function as normal will put it on a queue

Example:
    >>> import lox
    >>> @lox.process(4) # Will operate with a maximum of 4 processes
    >>> def foo(x,y):
    >>>     print("Foo: %d * %d" % (x,y))
    >>>     return x*y
    >>> 
    >>> foo(1)
    Foo: 3 * 4
    12
    >>> for i in range(5):
    >>>     foo.scatter(i, i+1)
    >>> 
    Foo: 0 * 1
    Foo: 1 * 2
    Foo: 2 * 3
    Foo: 3 * 4
    Foo: 4 * 5
    >>> results = foo.gather()
    >>> print(results)
    [0, 2, 6, 12, 20]
"""


from multiprocessing import Pool, Queue

__all__ = ['process',]

class _ProcessWorker(threading.Thread):
    def __init__(self):
        pass
    def run(self):
        pass

class _ProcessWrapper:
    """Process helper decorator

    Methods
    -------
    __call__( *args, **kwargs )
        Vanilla passthrough function execution. Default user function behavior.

    __len__()
        Returns the current job queue length

    scatter( *args, **kwargs)
        Start a job executing func( *args, **kwargs ).
        Workers are spun up automatically.
        Obtain results via gather()

    gather()
        Block until all jobs called via scatter() are complete.
        Returns a list of results in the order that scatter was invoked.
    """

    def __init__(self, n_workers, func):
        self.pool = Pool(n_workers)

        self.func       = func
        self.__name__   = func.__name__
        self.__doc__    = func.__doc__
        self.__module__ = func.__module__

        self.job_queue = Queue()

    def __len__(self):
        """ Return length of job queue """

        return self.job_queue.qsize()


    def __call__( *args, **kwargs ):
        """ Vanilla execute the wrapped function"""

        self.func( *args, **kwargs )

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary
        """
        self.pool.apply_async(self.func, (**args, **kwargs))

        # BELOW IS COPIED FROM THREADS

        self.job_ls.acquire() # will block if currently gathering
        self.response.append(None)
        self.job_queue.put(Job(len(self.response)-1,
                self.func, args, kwargs))
        self._create_worker()

    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other processes.
        Returns list of results in order scatter'd
        """
        with self.jobs_complete_lock: # Wait until all jobs are done
            response = list(self.response)
            self.response = deque()
        return response

def process(n_workers):
    """ Decorator to execute a function in multiple threads

    Example:
        >>> import lox
        >>> @lox.process(4) # Will operate with a maximum of 4 threads
        >>> def foo(x,y):
        >>>     print("Foo: %d * %d" % (x,y))
        >>>     return x*y
        >>> 
        >>> foo(1)
        Foo: 3 * 4
        12
        >>> for i in range(5):
        >>>     foo.scatter(i, i+1)
        >>> 
        Foo: 0 * 1
        Foo: 1 * 2
        Foo: 2 * 3
        Foo: 3 * 4
        Foo: 4 * 5
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
        Number of process workers to invoke.
    """

    def wrapper(func):
        return _ThreadWrapper(n_workers, func, daemon=daemon)

    return wrapper

if __name__ == '__main__':
    import doctest
    doctest.testmod()
