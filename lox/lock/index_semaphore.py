"""
.. module:: index_semaphore
   :synopsis: BoundedSemaphore where acquires return an index from [0, val).

.. moduleauthor:: Brian Pugh <bnp117@gmail.com>
"""

import logging as log
from contextlib import contextmanager
from queue import Empty, Full, Queue

__all__ = [
    "IndexSemaphore",
]


class IndexSemaphore:
    """``BoundedSemaphore``-like object where acquires return an index from [0, val).

    Example acquiring a gpu resource from a thread:
        >>> sem = IndexSemaphore(4)
        >>> with sem() as index:
        >>>     print("Obtained resource %d" % (index,))
        >>>
        Obtained resource 0
    """

    def __init__(self, val):
        """Create an ``IndexSemaphore`` object.

        Parameters
        ----------
        val : int
            Number of resources available.
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

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before aborting.
            Set timeout=None for no timeout.

        Returns
        -------
        int
            Resource index. None on timeout/failure.
        """

        index = self.acquire(timeout=timeout)
        try:
            yield index
        except Exception as e:
            log.error(e)
        finally:
            if index is not None:
                self.release(index)

    def __len__(self):
        """Return current blocked queue size.

        Returns
        -------
        int
            Current blocked queue size.
        """

        return self.queue.qsize()

    def acquire(self, timeout=None):
        """Blocking acquire resource.

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before returning.

        Returns
        -------
        int
            Resource index on successful acquire. None on timeout.
        """

        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None

    def release(self, index):
        """Release resource at index.

        Parameters
        ----------
        index : int
            Index of resource to release.

        Raises
        ------
        Exception
            Resource has been released more times than acquired.
        """

        try:
            self.queue.put_nowait(index)
        except Full:
            raise Exception("IndexSemaphore released more times than acquired")
