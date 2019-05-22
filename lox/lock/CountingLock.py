"""@package CountingLock

"""

import threading

__all__ = ["CountingLock",]

class CountingLock:
    """
    Acquires a provided lock while counter is nonzero.
    Releases provided lock when counter is zero.
    """
    def __init__(self, lock):
        """
        @param lock Lock to acquire when counter is nonzero; release when counter is 0
        """
        self._lock = lock
        self._counter = 0
        self._counter_lock = threading.RLock()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        with self._counter_lock:
            self._counter += 1
            if self._counter == 1:
                self._lock.acquire()

    def release(self):
        with self._counter_lock:
            self._counter -= 1
            if self._counter == 0:
                self._lock.release()

    def get_lock(self):
        return self._lock

    def get_count(self):
        with self._counter_lock:
            count = self._counter
        return count
