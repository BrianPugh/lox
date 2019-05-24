"""
.. module:: LightSwitch
   :synopsis: Lock acquire on first entry and release on last exit.

.. moduleauthor:: Brian Pugh <bnp117@gmail.com>

See https://w3.cs.jmu.edu/kirkpams/OpenCSF/Books/cs361/html/DesignAdv.html

"""

from threading import RLock

__all__ = ["LightSwitch",]

class LightSwitch:
    """Acquires a provided lock while LightSwitch is in use.

    The lightswitch pattern creates a first-in-last-out synchronization
    mechanism. The name of the pattern is inspired by people entering a
    room in the physical world. The first person to enter the room turns
    on the lights; then, when everyone is leaving, the last person to exit
    turns the lights off.

    Attributes
    ----------
    lock : threading.Lock
        The lock provided to the constructor that may be acquired/released
        by LightSwitch.

    counter: int
        Number of times the LightSwitch has been acquired without release.

    Methods
    -------
    acquire()
        Acquire the LightSwitch and increment the internal counter.
        When the internal counter is incremented from zero, it will acquire
        the provided lock.

    release()
        Release the LightSwitch by decrementing the internal counter.
        When the internal counter is decremented to zero, it will release
        the provided lock.
    """

    def __init__(self, lock):
        """Create a LightSwitch object.

        Parameters
        ----------
        lock : threading.Lock
            Lock to acquire when internal counter is incremented from zero.
            Lock to release when internal counter is decremented to zero.
        """

        self.lock = lock
        self.counter = 0
        self._counter_lock = RLock()

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
        """ Acquire LightSwitch at context enter """

        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Release LightSwitch at context exit """

        self.release()

    def __len__(self):
        """Get the counter value"""

        return self.counter

    def acquire(self):
        """Acquire the LightSwitch and increment the internal counter.

        When the internal counter is incremented from zero, it will acquire
        the provided lock.
        """

        with self._counter_lock:
            self.counter += 1
            if self.counter == 1:
                self._lock.acquire()

    def release(self):
        """Release the LightSwitch by decrementing the internal counter.

        When the internal counter is decremented to zero, it will release
        the provided lock.
        """

        with self._counter_lock:
            self.counter -= 1
            if self.counter == 0:
                self._lock.release()

