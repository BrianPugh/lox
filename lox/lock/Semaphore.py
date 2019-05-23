"""Semaphore
Similar to threading.Semaphore, but returns the index obtained.

Example use-case:
    You have 4 GPUs: [0,1,2,3].
    You have many threads that occasionally require a GPU for part of their algorithm.

    resource_semaphore = ResourceSemaphore
    with resource_semaphore
"""
import threading
from threading import Lock, BoundedSemaphore
from queue import Queue
from contextlib import contextmanager

__all__ = ["ResourceSemaphore",]

class ResourceSemaphore:
    """ Semaphore where each acquire returns a specific index from [0, val)
    """
    def __init__(self, val):
        self.queue = Queue(maxsize=val)
        for i in range(val):
            self.queue.put(i)

    @contextmanager
    def __call__(self, timeout=None):
        """
        Only call as part of a "with" statement.
        """
        try:
            index = self.acquire(timeout=timeout)
            yield index
        finally:
            if index is not None:
                self.release(index)

    def __enter__(self):
        print("meow")
        index = self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

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

