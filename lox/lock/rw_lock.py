"""
.. module:: rw_Lock
   :synopsis: Synchronization primitive to solves the readers–writers problem.

.. moduleauthor:: Brian Pugh <bnp117@gmail.com>
"""

from threading import Lock
from contextlib import contextmanager
from . import LightSwitch

__all__ = ["RWLock", ]


class RWLock:
    """Lock for a Multi-Reader-Single-Writer scenario.

    Unlimited numbers of reader can obtain the lock, but as soon as a writer
    attempts to acquire the lock, all reads are blocked until the current
    readers are finished, the writer acquires the lock, and finally 
    releases it.

    Similar to a ``lox.LightSwitch``, but blocks incoming "readers" while a "write"
    is trying to be performed.

    Attributes
    ----------
    read_counter : int
        Number of readers that have acquired the lock.
    """

    def __init__(self):
        """ Create RWLock object """

        self._no_writers    = Lock()
        self._no_readers    = Lock()
        self.read_counter   = LightSwitch(self._no_writers)
        self._write_counter = LightSwitch(self._no_readers)
        self._readers_queue = Lock()

    @contextmanager
    def __call__(self, rw_flag:str, timeout=-1):
        """ Used in contextmanager to specify acquire/release type """

        self.acquire(rw_flag, timeout=timeout)
        try:
            yield self
        finally:
            self.release(rw_flag)

    def __len__(self):
        """Get the read_counter value

        Returns
        -------
        int
           Number of current readers
        """

        return len(self.read_counter)

    def _check_rw_flag(self, rw_flag):
        """Checks if passed in flag is a valid value"""

        rw_flag = rw_flag.lower()
        if rw_flag == 'r':
            pass
        elif rw_flag == 'w':
            pass
        else:
            raise ValueError("rw_flag must be 'r' or 'w'")
        return rw_flag

    def acquire(self, rw_flag:str, timeout=-1):
        """ Acquire the lock as a "reader" or a "writer".

        Parameters
        ----------
        rw_flag : str
            Either 'r' for 'read' or 'w' for 'write' acquire.

        timeout : float
            Time in seconds before timeout occurs for acquiring lock.

        Returns
        -------
        bool
            ``True`` if lock was acquired, ``False`` otherwise.
        """

        obtained = False
        rw_flag = self._check_rw_flag(rw_flag)
        if rw_flag == 'r':
            obtained = self._readers_queue.acquire(timeout=timeout)
            if not obtained:
                return False

            obtained = self._no_readers.acquire(timeout=timeout)
            if not obtained:
                self._readers_queue.release()
                return False

            obtained = self.read_counter.acquire(timeout=timeout)

            self._no_readers.release()
            self._readers_queue.release()
        elif rw_flag == 'w':
            obtained = self._write_counter.acquire(timeout=timeout)
            if not obtained:
                return False

            obtained = self._no_writers.acquire(timeout=timeout)
            if not obtained:
                self._write_counter.release()
        return obtained

    def release(self, rw_flag:str):
        """Release acquired lock.

        Parameters
        ----------
        rw_flag : str
            Either 'r' for 'read' or 'w' for 'write' acquire.
        """

        rw_flag = self._check_rw_flag(rw_flag)
        if rw_flag == 'r':
            self.read_counter.release()
        elif rw_flag == 'w':
            self._no_writers.release()
            self._write_counter.release()

