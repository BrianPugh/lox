from abc import ABC, abstractmethod
from collections import deque
import threading
from ..exceptions import Timeout

from threading import Lock
import pathos.multiprocessing as mp

__all__ = ["WorkerWrapper", "ScatterPromise"]

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


class ScatterPromise(int):
    """ Represents: index into solution array
    Also provides the methods/data to chain scatter calls
    """

    def __new__(cls, val, queue, fulfill, sol_array):
        """
        Parameters
        ----------
        val : int
            Index of result into solution array
        queue : Queue()-like object
            Queue that decorate function results get put on. The same queue is
            passed to all promises made from the decorated function.
        fulfill : Lock()-like object
            Acquired lock that is released when results are available.
        sol_array : deque
            Array of solutions where sol_array[val] is the promised result.
        """
        if val < 0:
            raise ValueError("Value must be a non-negative index")
        new_obj = super(cls, cls).__new__(cls, val)
        new_obj.queue = queue
        new_obj.fulfill = fulfill
        new_obj.sol_array = sol_array
        return new_obj 

    def put(self, data, *args, **kwargs):
        """ Put data onto results queue. Should probably never be used. """
        return self.queue.put(data, *args, **kwargs)

    def get(self, *args, **kwargs):
        """ Get item from result queue. """
        return self.queue.pop(*args, **kwargs)

    def resolve(self, timeout=-1):
        """ Block until the result is ready. """

        if not self.fulfill.acquire(timeout=timeout):
            raise Timeout
        return self.sol_array[self]
