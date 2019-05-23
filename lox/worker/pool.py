"""@package Pool
Easily execute a function in multiple threads

Calling the decorated function as normal will put it on a queue

# Will operate with a maximum of 4 workers
@lox.pool(4)
def complex_function(x):
    sleep(10)

"""

import threading
from lox import LightSwitch
from threading import Lock, RLock, BoundedSemaphore
import queue
from queue import Queue
from functools import wraps
from collections import namedtuple, deque

__all__ = ["pool",]

Job = namedtuple('Job', ['index', 'func', 'args', 'kwargs',])
Response = namedtuple('Response', ['index'])

class _PoolWorker(threading.Thread):
    """Thread worker created on-demand by _PoolWrapper
    """

    def __init__(self, job_queue, res, worker_sem, lightswitch, **kwargs):
        self.job_queue = job_queue;
        self.res = res
        self.worker_sem = worker_sem
        self.lightswitch = lightswitch
        super().__init__(**kwargs)

    def run(self, timeout=1):
        """ Executes a Job and stores the results

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait while dequeuing a job.
            If no job is dequeued, worker will destroy itself.
        """

        while True:
            try:
                job = self.job_queue.get(timeout=timeout)
                self.res[job.index] = job.func(*job.args, **job.kwargs)
            except queue.Empty:
                break
            finally:
                self.lightswitch.release() # indicate job complete
        self.worker_sem.release() # indicate worker is terminated
        return

class _PoolWrapper:
    """Pool helper decorator

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

    def __init__(self, max_workers, func, daemon=None):
        """
        Creates the callable object for the 'pool' decorator

        Parameters
        ----------
        max_workers : int
            Maximum number of threads to invoke.

        func : function
            Function handle that each thread worker will execute
        """

        self.workers_sem = BoundedSemaphore(max_workers)

        self.func       = func
        self.__name__   = func.__name__
        self.__doc__    = func.__doc__
        self.__module__ = func.__module__

        self.daemon     = daemon

        self.job_queue = Queue()

        self.jobs_complete_lock = Lock()
        self.job_ls = LightSwitch(self.jobs_complete_lock) # Used to determine if all jobs have been completed

        self.response = deque() # Stores gather'd user function responses

    def __call__(self, *args, **kwargs):
        """ Vanilla execute the wrapped function"""

        return self.func(*args, **kwargs)

    def __len__(self):
        """ Return length of job queue """

        return self.job_queue.qsize()

    def _create_worker(self):
        """Create a worker if under maximum capacity"""

        if self.workers_sem.acquire(timeout=0):
            _PoolWorker(self.job_queue, self.response, self.workers_sem, self.job_ls, daemon=self.daemon).start()

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary
        """

        self.job_ls.acquire() # will block if currently gathering
        self.response.append(None)
        self.job_queue.put(Job(len(self.response)-1,
                self.func, args, kwargs))
        self._create_worker()

    def gather(self):
        """ Gather results. Blocks until job_queue is empty.
        Also blocks scatter on other threads.
        Returns list of results in order scatter'd
        """
        with self.jobs_complete_lock: # Wait until all jobs are done
            response = list(self.response)
            self.response = deque()
        return response

def pool(max_workers, daemon=None):
    """ Decorator to execute a function in multiple threads

    Example:
        >>> @lox.pool
        >>> def multiply(a,b):
        >>>    return a*b
        >>> multiply(3,4) # Function works as normal
        12
        >>> [multiply.scatter(x,y) for x,y in zip([2,3],[5,6])]
        >>> multiply.gather()
        [ 10, 18 ]

    Parameters
    ----------
    max_workers : int
        Maximum number of threads to invoke.
        When not specified, the wrapped function becomes the first argument
        and a default number of max_workers is used.
    """

    @wraps(func)
    def wrapper(func):
        return _PoolWrapper(max_workers, func, daemon=daemon)

    if isinstance(max_workers, int):
        # assume this is being called from decorator
        return wrapper
    else:
        func = max_workers
        max_workers = 50
        return _PoolWrapper(max_workers, func, daemon=daemon)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
