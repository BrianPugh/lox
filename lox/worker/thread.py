"""
.. module:: thread
   :synopsis: Easily execute a function in multiple threads.

Still allows the decorated function as normal.

Example:

.. doctest::

    >>> import lox
    >>>
    >>> @lox.thread(4) # Will operate with a maximum of 4 threads
    ... def foo(x,y):
    ...     return x*y
    >>> foo(3,4)
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i+1)
    -ignore-
    >>> # foo is currently being executed in 4 threads
    >>> results = foo.gather() # block until results are ready
    >>> print(results) # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]
"""

import threading
from .worker import WorkerWrapper
from threading import Lock, BoundedSemaphore
import queue
from collections import namedtuple, deque
from lox import LightSwitch

__all__ = ["thread", ]

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

class _ThreadWorker(threading.Thread):
    """Thread worker created on-demand by _ThreadWrapper
    """

    def __init__(self, job_queue, res, worker_sem, lightswitch, **kwargs):
        self.job_queue   = job_queue   # Queue to pop jobs off of
        self.res         = res         # deque object to place results in
        self.worker_sem  = worker_sem  # object to "release()" upon worker destruction 
        self.lightswitch = lightswitch # object to "release()" upon job completion
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
                # Allow worker to self-terminate
                break
            finally:
                self.lightswitch.release() # indicate job complete
        self.worker_sem.release() # indicate worker is terminated
        return

class _ThreadWrapper(WorkerWrapper):
    """Thread helper decorator
    """

    def __init__(self, n_workers, func, daemon=None):
        """
        Creates the callable object for the 'thread' decorator

        Parameters
        ----------
        n_workers : int
            Maximum number of threads to invoke.

        func : function
            Function handle that each thread worker will execute
        """
        super().__init__(n_workers, func)

        # Queue to put jobs on
        self.job_queue = queue.Queue()
        self.jobs_complete_lock = Lock()
        self.job_lightswitch = LightSwitch(self.jobs_complete_lock) # Used to determine if all jobs have been completed

        self.workers_sem = BoundedSemaphore(self.n_workers)
        self.daemon      = daemon

    def __len__(self):
        """ Return length of job queue """

        return self.job_queue.qsize()

    def _create_worker(self):
        """Create a worker if under maximum capacity"""

        if self.workers_sem.acquire(timeout=0):
            _ThreadWorker(self.job_queue, self.response, self.workers_sem, self.job_lightswitch, daemon=self.daemon).start()

    def scatter(self, *args, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary
        
        Return
        ------
            Index into the subsequent gather() results
        """

        self.job_lightswitch.acquire() # will block if currently gathering
        index = len(self.response)
        self.response.append(None)
        self.job_queue.put(Job(index, self.func, args, kwargs))
        self._create_worker()
        return index

    def gather(self):
        with self.jobs_complete_lock: # Wait until all jobs are done
            response = list(self.response)
            self.response = deque()
        return response


def thread(max_workers, daemon=None):
    """ Decorator to execute a function in multiple threads

    Example:

.. doctest::

        >>> import lox
        >>> 
        >>> @lox.thread(4) # Will operate with a maximum of 4 threads
        ... def foo(x,y):
        ...     return x*y
        >>> foo(3,4)
        12
        >>> for i in range(5):
        ...     foo.scatter(i, i+1)
        -ignore-
        >>> # foo is currently being executed in 4 threads
        >>> results = foo.gather()
        >>> print(results)
        [0, 2, 6, 12, 20]

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

    Parameters
    ----------
    max_workers : int
        Maximum number of threads to invoke.
        When not specified, the wrapped function becomes the first argument
        and a default number of max_workers is used.
    """

    def wrapper(func):
        return _ThreadWrapper(max_workers, func, daemon=daemon)

    if isinstance(max_workers, int):
        # assume this is being called from decorator like "lox.thread(5)"
        return wrapper
    else:
        # assume decorator with called as "lox.thread"
        func = max_workers
        max_workers = 50
        return _ThreadWrapper(max_workers, func)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
