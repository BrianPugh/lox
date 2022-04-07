"""
.. module:: QLock
   :synopsis: FIFO Lock

.. moduleauthor:: Brian Pugh <bnp117@gmail.com>
"""

from collections import deque
from threading import Lock

__all__ = [
    "QLock",
]


class QLock:
    """Lock that guarentees FIFO operation. ~6x slower than ``Lock()``.

    Modified from https://stackoverflow.com/a/19695878
    """

    def __init__(self):
        """Create a ``QLock`` object."""

        self.queue = deque()
        self.lock = Lock()
        self.count = 0

    def __enter__(self):
        """Acquire ``QLock`` at context enter."""

        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release ``QLock`` at context exit."""

        self.release()

    def __len__(
        self,
    ):
        """Return number of tasks waiting to acquire.

        Returns
        -------
        int
            Number of tasks waiting to acquire.
        """

        return self.count

    @property
    def locked(self):
        """Whether or not the ``QLock`` is acquired"""

        return self.count > 0

    def acquire(self, timeout=-1):
        """Block until resource is available.

        Threads that call ``acquire`` obtain resource FIFO.

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before aborting.

        Return
        ------
        bool
            True on successful acquire, False on timeout.
        """

        with self.lock:
            if self.count > 0:
                # Append a new acquired lock the queue
                lock = Lock()
                lock.acquire()
                self.queue.append(lock)
                self.lock.release()

                # Block until the lock has been released from another thread
                acquired = lock.acquire(timeout=timeout)
                self.lock.acquire()
                if acquired:
                    # lock acquired
                    pass
                else:
                    # timed out
                    try:
                        self.queue.remove(self.lock)
                    except ValueError:
                        # lock must have been released between the timeout
                        # and self.lock.acquire()
                        pass
                    return False
            self.count += 1
        return True

    def release(self):
        """Release exclusive access to resource.

        Raises
        ------
        ValueError
            Lock released more than it has been acquired.
        """

        with self.lock:
            if self.count == 0:
                raise ValueError("lock not acquired")
            self.count -= 1
            if self.queue:
                self.queue.popleft().release()
