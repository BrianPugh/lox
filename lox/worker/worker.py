from abc import ABC, abstractmethod
from collections import namedtuple, deque
from lox import LightSwitch

__all__ = ["WorkerWrapper", "Job", ]

""" Elements on the Job Queue

Attributes
----------
index
    index of results to store func's return value(s).
func
    function to execute
args
    positional arguments to feed into func
kwargs
    keyword arguments to feed into func
"""
Job = namedtuple('Job', ['index', 'func', 'args', 'kwargs',])

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

    @property
    def _lock_constructor(self):
        raise NotImplementedError

    @property
    def _queue_constructor(self):
        raise NotImplementedError

    def __init__(self, n_workers, func):
        # Maximum number of workers to spin up
        self.n_workers = n_workers

        # Function metadata
        self.func       = func
        self.__name__   = func.__name__
        self.__doc__    = func.__doc__
        self.__module__ = func.__module__

        # Queue to put jobs on
        self.job_queue = self._queue_constructor()
        self.jobs_complete_lock = self._lock_constructor()
        self.job_lightswitch = LightSwitch(self.jobs_complete_lock) # Used to determine if all jobs have been completed

        self.response = deque() # Stores gather'd user function responses

    def __call__(self, *args, **kwargs):
        """ Vanilla execute the wrapped function"""

        return self.func(*args, **kwargs)

    def __len__(self):
        """ Return length of job queue """

        return self.job_queue.qsize()

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary
        """
        self.job_lightswitch.acquire() # will block if currently gathering
        index = len(self.response)
        self.response.append(None)
        self.job_queue.put(Job(index, self.func, args, kwargs))
        return index

    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other threads.
        Returns list of results in order scatter'd
        """
        with self.jobs_complete_lock: # Wait until all jobs are done
            response = list(self.response)
            self.response = deque()
        return response


