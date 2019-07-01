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
        """ Vanilla execute the wrapped function. """

        return self.func(*args, **kwargs)

    @abstractmethod
    def __len__(self):
        """
        Returns
        -------
        int
            Length of unprocessed job queue.
        """

        return

    @abstractmethod
    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary.

        Returns
        -------
        int-like
            Index into solution array. May be a int-like promise for chaining.
        """
        return

    @abstractmethod
    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other threads.

        Returns
        -------
        list
            Results in order ``scatter``'d
        """
        return


class ScatterPromise(int):
    """ Represents: index into solution array.
    Also provides the functionality to chain scatter calls.
    """

    def __new__(cls, val, dec):
        """
        Parameters
        ----------
        val : int
            Index of result into solution array.
        dec : decorator object
            Decorator object.
        """

        if val < 0:
            raise ValueError("Value must be a non-negative index")
        new_obj = super(cls, cls).__new__(cls, val)
        new_obj.dec = dec # Decorator object
        return new_obj

