"""@package OneWriterManyReader
"""
import threading
from contextlib import contextmanager
from lox.lock.LightSwitch import LightSwitch

__all__ = ["OneWriterManyReader",]

class OneWriterManyReader:
    """
    Lock for a One-writer-Many-reader scenario.

    Starvation policy: Once the writer attempts to acquire the lock, all further
    reads will block until the writer acquires and subsequently releaases the lock.
    """
    def __init__(self):
        self._no_writers    = threading.Lock()
        self._no_readers    = threading.Lock()
        self._read_counter  = LightSwitch(self._no_writers)
        self._write_counter = LightSwitch(self._no_readers)
        self._readers_queue = threading.Lock()

    @contextmanager
    def __call__(self, rw_flag:str, timeout=-1):
        """
        Only call as part of a "with" statement.
        """
        self.acquire(rw_flag, timeout=timeout)
        try:
            yield self
        finally:
            self.release(rw_flag)

    def __len__(self):
        return len(self.read_counter)

    def _check_rw_flag(self, rw_flag):
        rw_flag = rw_flag.lower()
        if rw_flag == 'r':
            pass
        elif rw_flag == 'w':
            pass
        else:
            raise ValueError("rw_flag must be 'r' or 'w'")
        return rw_flag

    def acquire(self, rw_flag:str, timeout=-1):
        """ Acquire the lock either as a reader or a writer.
        @param rw_flag Either 'r' or 'w' for read/write acquire
        @param timeout Time in seconds before timeout occurs for acquiring lock
        @return True if lock was acquired; False otherwise
        """
        rw_flag = self._check_rw_flag(rw_flag)
        if rw_flag == 'r':
            with self._readers_queue:
                with self._no_readers:
                    self._read_counter.acquire()
        elif rw_flag == 'w':
            self._write_counter.acquire()
            self._no_writers.acquire()
        return True

    def release(self, rw_flag:str):
        """Release acquired lock
        @param rw_flag Either 'r' or 'w' for read/write acquire
        """
        rw_flag = self._check_rw_flag(rw_flag)
        if rw_flag == 'r':
            self._read_counter.release()
        elif rw_flag == 'w':
            self._no_writers.release()
            self._write_counter.release()

