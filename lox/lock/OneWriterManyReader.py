"""@package OneWriterManyReader
"""

import threading
from contextlib import contextmanager
from lox.lock.LightSwitch import LightSwitch

__all__ = ["OneWriterManyReader",]

class OneWriterManyReader:
    """Lock for a One-writer-Many-reader scenario.

    Unlimited numbers of reader can obtain the lock, but as soon as a writer
    attempts to acquire the lock, all reads are blocked until the current readers
    are finished, the writer acquires the lock, and finally releases it.

    Attributes
    ----------
    read_counter : int
        Number of readers that have acquired the lock.

    Methods
    -------
    acquire(rw_flag:str)
        Acquire the lock as a "reader" or a "writer"

    release(rw_flag:str)
        Release the lock as a "reader" or a "writer"

    """
    def __init__(self):
        self._no_writers    = threading.Lock()
        self._no_readers    = threading.Lock()
        self.read_counter  = LightSwitch(self._no_writers)
        self._write_counter = LightSwitch(self._no_readers)
        self._readers_queue = threading.Lock()

    @contextmanager
    def __call__(self, rw_flag:str, timeout=-1):
        """ Used in contextmanager to specify acquire/release type """

        self.acquire(rw_flag, timeout=timeout)
        try:
            yield self
        finally:
            self.release(rw_flag)

    def __len__(self):
        """Get the read_counter value"""

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
            TODO: Time in seconds before timeout occurs for acquiring lock.

        Returns
        -------
            True if lock was acquired, False otherwise
        """

        rw_flag = self._check_rw_flag(rw_flag)
        if rw_flag == 'r':
            with self._readers_queue:
                with self._no_readers:
                    self.read_counter.acquire()
        elif rw_flag == 'w':
            self._write_counter.acquire()
            self._no_writers.acquire()
        return True

    def release(self, rw_flag:str):
        """Release acquired lock

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

