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
from ..queue import Announcement
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
    pre_args
        positional arguments to feed into func before promised results (if available)
    post_args
        positional arguments to feed into func after promised results (if available)
    kwargs
        keyword arguments to feed into func
    """

    def __init__(self, index, func, pre_args, post_args, kwargs):
        self.index = index
        self.func = func
        self.pre_args = pre_args
        self.args = ()
        self.post_args = post_args
        self.kwargs = kwargs

    def __str__(self):
        return "(index=%s, func=%s, pre_args=%s, args=%s, post_args=%s, kwargs=%s)" % \
                ( str(self.index), str(self.func),
                        str(self.pre_args), str(self.args), str(self.post_args)
                        , str(self.kwargs) )

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
                    log.debug("Executing decorated function %s with pre_args %s, args %s, post_args %s, and kwargs %s" \
                            % (str(job.func), str(job.pre_args), str(job.args), str(job.post_args), str(job.kwargs)))
                    self.res[job.index] = job.func(*job.pre_args, *job.args, *job.post_args, **job.kwargs)
                except Exception as e:
                    with term_colors("red"):
                        print(traceback.format_exc())
                finally:
                    result = Result(job.index, self.res[job.index])
                    log.debug("Placing %s onto res_queue %s" % (str(result), str(self.res_queue)))
                    self.res_queue.put(result)
                    self.lightswitch.release() 
            except queue.Empty:
                # Allow worker to self-terminate
                break
        self.worker_sem.release() # indicate worker is terminated
        return

class _PromiseForwarder(threading.Thread):
    """ Forwards Promises from the announcement to the job queue. """

    sleep_time = 0.01

    def __init__( self, thread_wrapper, **kwargs ):
        """ Create a _PromiseForwarder object

        Parameters
        ----------
        thread_wrapper : _ThreadWrapper
            decorator of current processing function
        """

        super().__init__(**kwargs)
        self.thread_wrapper = thread_wrapper
        self._kill = False

    def run(self,):
        while True:
            if self._kill:
                break

            if self.thread_wrapper.prev_promise is None:
                break

            # Get a result from the previous stage
            log.debug("Trying to get from res_queue %s" % (str(self.thread_wrapper.prev_promise_q),))
            try:
                # Timeout so we can poll the self._kill attribute
                result = self.thread_wrapper.prev_promise_q.get(timeout=1)
            except queue.Empty:
                continue
            log.debug("Popped result %s" % str(result))

            # Get the job
            # Need to loop incase worker threads are faster than main thread
            for i in range(10):
                try:
                    job = self.thread_wrapper.jobs[result.index]
                    break
                except Exception as e:
                    log.warning(e)
                    sleep(self.sleep_time)
            else:
                # Failure
                log.error("Failed to obtain job at %d" % result.index)
                continue
            log.debug("PromiseForwarder: Retrieved job %s" % str(job))

            # Insert the previous results into the new job's args
            if self.thread_wrapper.auto_unpack:
                if isinstance(result.value, tuple):
                    job.args = result.value
                else:
                    job.args = (result.value,)
            else:
                log.debug("Not auto-unpacking")
                job.args = (result.value,)

            log.debug("PromiseForwarder: forwarding job %s" % str(job))
            self.thread_wrapper._dispatch_job(job)
        log.debug("PromiseForwarder Exiting")
        return

    def kill(self):
        """ Sets a flag that the worker periodically checks. When detected,
        worker will destroy itself.
        """

        self._kill = True


class _ThreadWrapper(WorkerWrapper):
    """Thread helper decorator.
    """

    def __init__(self, func, n_workers=50, daemon=None):
        """
        Creates the callable object for the 'thread' decorator.

        Parameters
        ----------
        func : function
            Function handle that each thread worker will execute.

        n_workers : int
            Maximum number of threads to invoke.

        """
        super().__init__(n_workers, func)

        self.job_queue = queue.Queue() # Queue to put jobs on
        self.jobs_complete_lock = Lock()
        self.job_lightswitch = LightSwitch(self.jobs_complete_lock) # Used to determine if all jobs have been completed

        self.workers_sem = BoundedSemaphore(self.n_workers)
        self.daemon      = daemon
        self.enable_auto_unpacking()

        self.clear()

    def clear(self):
        log.debug("_ThreadWrapper clearing")
        self.res_queue = Announcement(backlog=0) # Queue to put results on
        self.promise_forwarder = None  # Thread handle for the promise forwarding task
        self.promises = deque()        # List of promises
        self.jobs = deque()            # list of jobs;
        self.response = deque()
        self.prev_promise = None       # In chaining, a previous chain's promise
        self.prev_promise_q = None

    def disable_auto_unpacking(self):
        """ Automatically unpack previously chained input tuples. 
        Enabled by default.
        """

        self.auto_unpack = False

    def enable_auto_unpacking(self):
        """ Do not unpack previously chained input tuples. """

        self.auto_unpack = True

    def __len__(self):
        """ 
        Returns
        -------
            Length of unprocessed job queue.
        """

        return self.job_queue.qsize()

    def _create_worker(self):
        """ Create a worker if under maximum capacity. """

        if self.workers_sem.acquire(timeout=0):
            _ThreadWorker(self.job_queue, self.res_queue, self.response,
                    self.workers_sem, self.job_lightswitch, daemon=self.daemon).start()

    def _create_promise_forwarder(self):
        """ Create promise forwarding thread. """

        if self.promise_forwarder is None:
            log.debug("Creating promise forwarder thread")
            self.promise_forwarder = _PromiseForwarder(self,)
            self.promise_forwarder.start()

    def _dispatch_job(self, job):
        self.job_queue.put(job)
        self._create_worker() # Create a thread if we are not at capacity

    def scatter(self, *args, detect_chaining=True, **kwargs):
        """Enqueue a job to be processed by workers.
        Spin up workers if necessary.

        Return
        ------
            Index into the subsequent gather() results
        """
        self.job_lightswitch.acquire()
        index = len(self.response)
        self.response.append(None)

        promise = ScatterPromise(index, self)
        self.promises.append(promise)

        # Detect if these are actual arguments or a single promise (implies chaining)
        prev_promise = None
        if detect_chaining:
            pre_args, post_args = [], []
            for arg in args:
                if isinstance(arg, ScatterPromise):
                    if prev_promise:
                        raise ValueError("There can only be one promise. If your input takes more than one promise, you should probably be calling \"gather()\"")
                    else:
                        prev_promise = arg
                    continue
                if prev_promise is not None:
                    post_args.append(arg)
                else:
                    pre_args.append(arg)
            pre_args = tuple(pre_args)
            post_args = tuple(post_args)
        else:
            pre_args = args
            post_args = ()

        job = Job(index, self.func, pre_args, post_args, kwargs)
        self.jobs.append(job)

        if prev_promise is not None:
            if self.prev_promise is None:
                self.prev_promise_q = prev_promise.dec.res_queue.subscribe()
                self.prev_promise = prev_promise
        else:
            self._dispatch_job(job)

        if self.prev_promise is not None:
            self._create_promise_forwarder()

        return promise

    def _finalize(self):
        """ Finalize self.res_queue and previous chain. """

        self.res_queue.finalize()
        if self.prev_promise is not None:
            self.prev_promise.dec._finalize()

    def gather(self):
        """ Block and collect results from prior ``scatter`` calls.
        """

        log.debug("Gathering %s" % (str(self.func),))

        # Save res_queue backlog memory
        self._finalize()

        with self.jobs_complete_lock: # Wait until all jobs are done
            log.debug("Gathering %s: jobs_complete_lock acquired" % (str(self.func)))
            response = list(self.response)

            if self.promise_forwarder is not None:
                log.debug("Gathering previous %s" % (str(self.prev_promise.dec.func),))

                self.promise_forwarder.kill()
                self.promise_forwarder = None
                self.prev_promise.dec.gather()

            # Clear internal results
            self.clear()

        return response


def thread(max_workers, daemon=None):
    """ Decorator to execute a function in multiple threads.

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

    Multiple decorated functions can be chained together, each function drawing
    from their own pool of threads. Functions that return tuples will automatically
    unpack into the chained function. Positional arguments and keyword arguments
    can be passed in as they normally would.

    .. doctest::
        >>> @lox.thread(2) # Will operate with a maximum of 2 threads
        ... def bar(x,y):
        ...     return x + y

        >>>  for i in range(5):
        ...    foo_res = foo.scatter(i, i+1)
        ...    bar.scatter(foo_res, 10) # scatter will automatically unpack the results of foo 
        >>>  
        >>> results = bar.gather() 

    Currently, a ``scatter`` call can have a maximum of 1 previous ``scatter``
    result as an input argument. However, unlimited number of functions can 
    be chained together in any topology.

    Parameters
    ----------
    max_workers : int
        Maximum number of threads to invoke.
        When ``lox.thread`` is called without ``()``, the wrapped function 
        a default number of max_workers is used (50).

    Methods
    -------
    __call__( *args, **kwargs )
        Vanilla passthrough function execution. Default user function behavior.

        Returns
        -------
        Decorated function return type.
           Return of decorated function.

    __len__()
        Returns
        -------
        int
            Current job queue length. Number of jobs that are currently waiting
            for an available worker.

    scatter( *args, **kwargs)
        Start a job executing decorated function ``func( *args, **kwargs )``.
        Workers are created and destroyed automatically.

        Returns
        -------
        int
            Solution's index into the results obtained via ``gather()``.

    gather()
        Block until all jobs called via ``scatter()`` are complete.

        Returns
        -------
        list
            Results in the order that scatter was invoked.

    disable_auto_unpacking()
        Automatically unpack previously chained input tuples.

    enable_auto_unpacking()
        Do not unpack previously chained input tuples.

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
