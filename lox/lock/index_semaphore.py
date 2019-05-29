"""
.. module:: index_semaphore
   :synopsis: BoundedSemaphore where acquires return an index from [0, val)

.. moduleauthor:: Brian Pugh <bnp117@gmail.com>
"""

from queue import Queue, Empty, Full
from contextlib import contextmanager

__all__ = ["IndexSemaphore", ]


class IndexSemaphore:
    """ BoundedSemaphore where acquires return an index from [0, val)

    Example usecase: thread acquiring a GPU

    Methods
    -------
    __call__(timeout=None)
        Enter context manager when a timeout wants to be specified.

    __len__()
        Returns the number of 'free' resources.

    acquire(timeout=None)
        Returns the index between [0, val) of the acquired resource.

    release(index)
        Release the resource at index.
    """

    def __init__(self, val):
        """Create an IndexSemaphore object

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
            >>> sem = IndexSemaphore(4)
            >>> with sem(timeout=1) as index:
            >>>     print("Obtained resource %d" % (index,))
            >>> 
            Obtained resouce 0

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before aborting.
            Returns None on timeout.
            Set timeout=None for no timeout.
        """

        index = self.acquire(timeout=timeout)
        try:
            yield index
        except Exception as e:
            print(e)
        finally:
            if index is not None:
                self.release(index)

    def __len__(self):
        return self.queue.qsize()

    def acquire(self, timeout=None):
        """Blocking acquire resource

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before returning

        Returns
        ----------
            Resource index on successful acquire. None on timeout
        """

        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None

    def release(self, index):
        """ Release resource at index

        Parameters
        ----------
        index : int
            Index of resource to release
        """

        try:
            self.queue.put_nowait(index)
        except Full:
            raise Exception("IndexSemaphore released more times than acquired")
