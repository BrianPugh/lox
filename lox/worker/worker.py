from abc import ABC, abstractmethod
from collections import deque

__all__ = ["WorkerWrapper", ]

class WorkerWrapper(ABC):
    """Worker helper decorator

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
        # Maximum number of workers to spin up
        self.n_workers = n_workers

        # Function metadata
        self.func       = func
        self.__name__   = func.__name__
        self.__doc__    = func.__doc__
        self.__module__ = func.__module__

        self.response = deque() # Stores gather'd user function responses

    def __call__(self, *args, **kwargs):
        """ Vanilla execute the wrapped function"""

        return self.func(*args, **kwargs)

    @abstractmethod
    def __len__(self):
        """ Return length of job queue """

        return

    @abstractmethod
    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary
        """
        return

    @abstractmethod
    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other threads.
        Returns list of results in order scatter'd
        """
        return


