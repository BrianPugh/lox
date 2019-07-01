"""
.. module:: LightSwitch
   :synopsis: Lock acquire on first entry and release on last exit.

.. moduleauthor:: Brian Pugh <bnp117@gmail.com>

See https://w3.cs.jmu.edu/kirkpams/OpenCSF/Books/cs361/html/DesignAdv.html

"""

import threading
import pathos.multiprocessing as mp
from time import time

__all__ = ["LightSwitch", ]


class LightSwitch:
    """Acquires a provided lock while ``LightSwitch`` is in use.

    The lightswitch pattern creates a first-in-last-out synchronization
    mechanism. The name of the pattern is inspired by people entering a
    room in the physical world. The first person to enter the room turns
    on the lights; then, when everyone is leaving, the last person to exit
    turns the lights off.

    Attributes
    ----------
    lock : threading.Lock
        The lock provided to the constructor that may be acquired/released
        by ``LightSwitch``.

    counter: int
        Number of times the ``LightSwitch`` has been acquired without release.
    """

    def __init__(self, lock, multiprocessing=False):
        """Create a ``LightSwitch`` object.

        Parameters
        ----------
        lock : ``threading.Lock`` or ``pathos.multiprocessing.Lock``
            Lock to acquire when internal counter is incremented from zero.
            Lock to release when internal counter is decremented to zero.
        """

        if multiprocessing:
            self._library = mp
        else:
            self._library = threading

        self.lock = lock
        self.counter = 0
        self._counter_lock = self._library.Lock()

    @property
    def lock(self):
        return self._lock

    @lock.setter
    def lock(self, lock):
        self._lock = lock

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, counter):
        self._counter = counter

    def __enter__(self):
        """ Acquire ``LightSwitch`` at context enter. """

        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Release ``LightSwitch`` at context exit. """

        self.release()

    def __len__(self):
        """Get the counter value.

        Returns
        -------
        int
            counter value (number of times lightswitch has been acquired).
        """

        return self.counter

    def acquire(self, timeout=-1):
        """Acquire the ``LightSwitch`` and increment the internal counter.

        When the internal counter is incremented from zero, it will acquire
        the provided lock.

        Parameters
        ----------
        timeout : float
            Maximum number of seconds to wait before aborting.

        Returns
        -------
        bool
            ``True`` on success, ``False`` on failure (like timeout).
        """

        # Acquire the counter_lock while keeping track of approximately time
        t_start = time()
        if not self._counter_lock.acquire(timeout=timeout):
            return False
        t_remaining = timeout - (time() - t_start)

        if timeout < 0:
            t_remaining = -1
        elif t_remaining < 0:
            t_remaining = 0

        # Acquire lock if first to acquire
        if self.counter == 0:
            if not self._lock.acquire(timeout=t_remaining):
                self._counter_lock.release()
                return False
        self.counter += 1

        self._counter_lock.release()
        return True

    def release(self):
        """Release the ``LightSwitch`` by decrementing the internal counter.

        When the internal counter is decremented to zero, it will release
        the provided lock.
        """

        with self._counter_lock:
            self.counter -= 1
            if self.counter == 0:
                self._lock.release()
