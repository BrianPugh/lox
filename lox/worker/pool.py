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
    _timeout = 1
    def __init__(self, job_queue, res, worker_sem, lightswitch, **kwargs):
        self.job_queue = job_queue;
        self.res = res
        self.worker_sem = worker_sem
        self.lightswitch = lightswitch
        super().__init__(**kwargs)

    def run(self,):
        while True:
            try:
                job = self.job_queue.get(timeout=1)
                self.res[job.index] = job.func(*job.args, **job.kwargs)
            except queue.Empty:
                break
            finally:
                self.lightswitch.release() # indicate job complete
        self.worker_sem.release() # indicate worker is terminated
        return

class _PoolWrapper:
    def __init__(self, max_workers, func, daemon=None):
        """
        @param max_workers Maximum number of threads to deploy
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
        """ vanilla execute the wrapped function
        """
        return self.func(*args, **kwargs)

    def __len__(self):
        """Return length of job queue
        """
        return self.job_queue.qsize()

    def _create_worker(self):
        """
        Create a worker if under maximum capacity
        """
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
    def wrapper(func):
        return _PoolWrapper(max_workers, func, daemon=daemon)

    if isinstance(max_workers, int):
        # assume this is being called from decorator
        return wrapper
    else:
        func = max_workers
        max_workers = 50
        return _PoolWrapper(max_workers, func, daemon=daemon)

