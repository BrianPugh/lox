"""
.. module:: thread
   :synopsis: Easily execute a function or method in multiple threads.

Still allows the decorated function/method as normal.

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

from collections import namedtuple, deque
from threading import Lock, BoundedSemaphore
import logging as log
import queue
import threading
from time import time, sleep
import traceback
import sys
from ..lock import LightSwitch
from ..helper import auto_adapt_to_methods, MethodDecoratorAdaptor, term_colors
from .worker import WorkerWrapper, ScatterPromise

__all__ = ["thread", ]

class Job:
    """ Elements on the Job Queue

    Attributes
    ----------
    index
        index of results to store func's return value(s).
    func
        function to execute
    complete
        synchronization object to release upon Job completion
    args
        positional arguments to feed into func
    kwargs
        keyword arguments to feed into func
    """

    def __init__(self, index, func, complete, args, kwargs):
        self.index = index
        self.func = func
        self.complete = complete
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return "(index=%s, func=%s, complete=%s, args=%s, kwargs=%s)" % \
                (str(self.index), str(self.func), str(self.complete), str(self.args), str(self.kwargs))

Result = namedtuple('Result', ['index', 'value',])

class _ThreadWorker(threading.Thread):
    """Thread worker created on-demand by _ThreadWrapper
    """

    def __init__(self, job_queue, res_queue, res, worker_sem, lightswitch, **kwargs):
        self.job_queue   = job_queue   # Queue to pop jobs off of
        self.res_queue   = res_queue   # Queue to push results onto
        self.res         = res         # deque object to place results in
        self.worker_sem  = worker_sem  # object to "release()" upon worker destruction
        self.lightswitch = lightswitch # object to "release()" upon job completion
        super().__init__(**kwargs)

    def run(self, ):
        """ Executes a Job and stores the results

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait while dequeuing a job.
            If no job is dequeued, worker will destroy itself.
        """

        while True:
            try:
                job = self.job_queue.get(timeout=0)
                try:
                    log.debug("Executing decorated function %s with args %s and kwargs %s" \
                            % (str(job.func), str(job.args), str(job.kwargs)))
                    self.res[job.index] = job.func(*job.args, **job.kwargs)
                except Exception as e:
                    with term_colors("red"):
                        print(traceback.format_exc())
                finally:
                    result = Result(job.index, self.res[job.index])
                    log.debug("Placing %s onto res_queue" % str(result))
                    self.res_queue.put(result)

                    # indicate job complete
                    job.complete.release()
                    self.lightswitch.release() 
            except queue.Empty:
                # Allow worker to self-terminate
                break
        self.worker_sem.release() # indicate worker is terminated
        return

class _PromiseForwarder(threading.Thread):
    sleep_time = 0.01
    def __init__( self, thread_wrapper, **kwargs ):
        super().__init__(**kwargs)
        self.thread_wrapper = thread_wrapper
        self._kill = False

    def run(self,):
        while True:
            if self._kill:
                break

            try:
                result = self.thread_wrapper.prev_queue.get(timeout=1)
            except queue.Empty:
                continue
            log.debug("Popped result %s" % str(result))

            prev_chain_res = result.value

            # Need to loop incase worker threads are faster than main thread
            for i in range(10):
                try:
                    job = self.thread_wrapper.jobs[result.index]
                    break
                except Exception as e:
                    log.warn(e)
                    sleep(self.sleep_time)
            else:
                # Failure
                log.error("Failed to obtain job at %d" % result.index)
                continue
            log.debug("PromiseForwarder: Retrieved job %s" % str(job))

            # Insert the previous results into the new job's args
            # todo: insert this at the same position the promise was fed in
            job.args = result.value + job.args

            log.debug("PromiseForwarder: forwarding job %s" % str(job))
            self.thread_wrapper.dispatch_job(job)

        return

    def kill(self):
        self._kill = True


class _ThreadWrapper(WorkerWrapper):
    """Thread helper decorator
    """

    def __init__(self, func, n_workers=50, daemon=None):
        """
        Creates the callable object for the 'thread' decorator

        Parameters
        ----------
        func : function
            Function handle that each thread worker will execute

        n_workers : int
            Maximum number of threads to invoke.

        """
        super().__init__(n_workers, func)

        self.job_queue = queue.Queue() # Queue to put jobs on
        self.res_queue = queue.Queue() # Queue to put results on
        self.jobs_complete_lock = Lock()
        self.job_lightswitch = LightSwitch(self.jobs_complete_lock) # Used to determine if all jobs have been completed

        self.workers_sem = BoundedSemaphore(self.n_workers)
        self.daemon      = daemon

        self.promise_forwarder = None # Thread handle for the promise forwarding task
        self.promises = deque()       # List of promises
        self.jobs = deque()           # list of jobs; todo: make a promise include job
        self.prev_queue = None        # In chaining, the previous chain's result queue

    def __len__(self):
        """ Return length of job queue """

        return self.job_queue.qsize()

    def _create_worker(self):
        """Create a worker if under maximum capacity"""

        if self.workers_sem.acquire(timeout=0):
            _ThreadWorker(self.job_queue, self.res_queue, self.response,
                    self.workers_sem, self.job_lightswitch, daemon=self.daemon).start()

    def _create_promise_forwarder(self):
        if self.promise_forwarder is None:
            # Create promise forwarding thread
            self.promise_forwarder = _PromiseForwarder(self,)
            self.promise_forwarder.start()

    def dispatch_job(self, job):
        self.job_queue.put(job)
        self._create_worker() # Create a thread if we are not at capacity

    def scatter(self, *args, detect_chaining=True, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary

        Return
        ------
            Index into the subsequent gather() results
        """
        self.job_lightswitch.acquire()
        index = len(self.response)
        self.response.append(None)
        job_complete = Lock()
        job_complete.acquire()

        promise = ScatterPromise(index, self.res_queue, job_complete, self.response)
        self.promises.append(promise)


        # Detect if these are actual arguments or a single promise (implies chaining)
        if detect_chaining and len(args) > 0 and isinstance(args[0], ScatterPromise):
            job = Job(index, self.func, job_complete, (), {}) # todo; use args kwargs
            self.jobs.append(job)
            if self.prev_queue is None:
                self.prev_queue = args[0].queue
            self._create_promise_forwarder()
        else:
            job = Job(index, self.func, job_complete, args, kwargs)
            self.jobs.append(job)
            self.dispatch_job(job)

        return promise

    def gather(self):
        with self.jobs_complete_lock: # Wait until all jobs are done
            response = list(self.response)

            # Clear internal results
            self.response = deque()
            self.res_queue = queue.Queue()
            self.promises = deque()
            self.jobs = deque()

            if self.promise_forwarder is not None:
                self.promise_forwarder.kill()
                self.promise_forwarder = None

            self.prev_queue = None

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
        Start a job executing `func( *args, **kwargs )`.
        Workers are spun up automatically.
        Obtain results via `gather()`.

    gather()
        Block until all jobs called via `scatter()` are complete.
        Returns a list of results in the order that scatter was invoked.

    Parameters
    ----------
    max_workers : int
        Maximum number of threads to invoke.
        When not specified, the wrapped function becomes the first argument
        and a default number of max_workers is used.
    """

    @auto_adapt_to_methods
    def wrapper(func):
        return _ThreadWrapper(func, n_workers=max_workers, daemon=daemon)

    if isinstance(max_workers, int):
        # assume this is being called from decorator like "lox.thread(5)"
        return wrapper
    else:
        # assume decorator with called as "lox.thread"
        func = max_workers
        return MethodDecoratorAdaptor(_ThreadWrapper, func)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
