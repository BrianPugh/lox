"""Semaphore
"""

import threading
from threading import Lock, BoundedSemaphore
from queue import Queue
from contextlib import contextmanager

__all__ = ["ResourceSemaphore",]

class ResourceSemaphore:
    """ BoundedSemaphore where acquires return an index from [0, val)

    Example usecase: thread acquiring a GPU

    Methods
    -------
    __call__(timeout=None)
        Enter context manager when a timeout wants to be specified.

    __enter__()
        Context manager enter with no arguments.

    __len__()
        Returns the number of 'free' resources.

    acquire(timeout=None)
        Returns the index between [0, val) of the acquired resource.

    release(index)
        Release the resource at index.
    """

    def __init__(self, val):
        """Create a ResourceSemaphore object

        Parameters
        ----------
        val : int
            Number of resources available
        """
        if val <= 0:
            raise ValueError("val must be >0")

        self.queue = Queue(maxsize=val)
        for i in range(val):
            self.queue.put(i)

    @contextmanager
    def __call__(self, timeout=None):
        """Enter context manager when a timeout wants to be specified.

        Only to be call as part of a "with" statement.

        Example:
            >>> resource_semaphore = ResourceSemaphore(4)
            >>> with resource_semaphore(timeout=1) as index:
            >>>     print("Obtained resource %d" % (index,)) # >"Obtained resource 0"
            >>>
            Obtained resouce 0

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before aborting.
            Returns None on timeout.
            Set timeout=None for no timeout.
        """

        try:
            index = self.acquire(timeout=timeout)
            yield index
        finally:
            if index is not None:
                self.release(index)

    def __enter__(self):
        """Context manager enter with no arguments.

        Example:
            >>> resource_semaphore = ResourceSemaphore(4)
            >>> with resource_semaphore as index:
            >>>     print("Obtained resource %d" % (index,)) # >"Obtained resource 0"
            >>>
            Obtained resouce 0
        """

        return self.__call__().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __len__(self):
        return self.queue.qsize()

    def acquire(self, timeout=None):
        """
        Returns -1 on timeout
        """
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return -1

    def release(self, index):
        try:
            self.queue.put_nowait(index)
        except queue.Full:
            raise Exception("ResourceSemaphore released more times than acquired")

