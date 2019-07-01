"""
.. module:: announcement
   :synopsis: Queue elements for multiple recipients.
"""


import queue
from collections import deque
import threading
import logging as log

__all__ = ["Announcement", "SubscribeFinalizedError", ]

class SubscribeFinalizedError(Exception):
    """ Raised when an Announcement.subscribe has been called,
    but the Announcement has already been finalized.
    """

    pass

class Announcement:
    """ Push to many queues with backlog support.

    Allows the pushing of data to many threads.

    Example:

    .. doctest::

        >>> import lox
        >>> ann = lox.Announcement()
        >>> foo_q = ann.subscribe()
        >>> bar_q = ann.subscribe()
        >>> 
        >>> @lox.thread
        ... def foo():
        ...     x = foo_q.get()
        ...     return x
        >>> 
        >>> @lox.thread
        ... def bar():
        ...     x = bar_q.get()
        ...     return x**2
        >>> 
        >>> ann.put(5)
        >>> foo.scatter()
        >>> foo_res = foo.gather()
        >>> bar.scatter()
        >>> bar_res = bar.gather()

    The backlog allows future (or potentially race-condition) subscribers to 
    get content put'd before they subscribed. However, the user must be careful 
    of memory consumption.

    Attributes
    ----------
    backlog : deque
        Backlog of queued data. None if not used.
    """

    @property
    def final(self,):
        return self._final

    @final.setter
    def final(self, val : bool):
        with self.lock:
            self._final = val

    @property
    def backlog(self,):
        return self._backlog

    @backlog.setter
    def backlog(self, val):
        self._backlog = val

    def __repr__(self,):
        with self.lock:
            qs = [str(q) for q in self.subscribers]
            string = super().__repr__() + ' with subscribers ' + ','.join(qs)
        return string

    def __init__(self, maxsize=0, backlog=None):
        """ Create an Announcement object.

        Parameters
        ----------
        maxsize : int
            Created queue's default maximum size. Defaults to 0 (no size limit).

        backlog : int
            Create a log of previously put data. New subscribers get the entire 
            backlog pushed onto their queue. Memory usage potentially unbounded.

            A value <=0 specifies unbounded backlog size. A value >0 specifies 
            a circular buffer.

            Defaults to None (backlog not used).

            Note: If used, it is recommended to use the ``finalize()`` method so
            that the backlog can be free'd when no longer necessary.
        """

        log.debug("Creating Announcement %X" % id(self))

        # General Attributes #
        self.subscribers = deque()
        self.maxsize = maxsize
        self.lock = threading.RLock()

        # Backlog objects #
        self.backlog_use = False if backlog is None else True
        self.final = False
        if self.backlog_use:
            if backlog <= 0:
                backlog = None
            self.backlog = deque(maxlen=backlog)
        else:
            self.backlog = None


    def __len__(self,):
        """ Get the number of subscribers.

        Returns
        -------
        int
            Number of subcribers.
        """

        return len(self.subscribers)

    def put(self, data, *args, **kwargs):
        """ Push data to all subscribed queues.

        Parameters
        ----------
        data : object
            Data to put on the queue.
        """
        with self.lock:
            for q in self.subscribers:
                q.put(data, *args, **kwargs)
            if self.backlog_use and not self.final:
                self.backlog.append(data)

    def subscribe(self, q=None, maxsize=None, *args, **kwargs):
        """ Subscribe to announcements.

        Parameters
        ----------
        q : Queue
            Existing queue to add to the subscribers' list.
            If not provided, a queue is created.

        maxsize : int
            Created queue's maximum size. Overrides Announcement's default 
            maximum size. Ignored if ``q`` is provided.

        Returns
        -------
        Queue
            Queue-like object for receiver to ``get`` data from.
        """

        with self.lock:
            if self.final:
                log.error("%s Subscribe when announcement already finalized" % (self,))
                raise SubscribeFinalizedError

            if q is None:
                # Create Queue
                if maxsize is None:
                    maxsize = self.maxsize
                q = queue.Queue( maxsize=maxsize )
            self.subscribers.append(q)
            if self.backlog_use:
                for x in self.backlog:
                    q.put(x, *args, **kwargs)
        return q

    def unsubscribe(self, q):
        """ Remove the queue from queue-list. Will no longer receive announcements.

        Parameters
        ----------
        q : Queue
            Queue object to remove.

        Raises
        ------
        ValueError
            ``q`` was not a subscriber.
        """

        with self.lock:
            self.subscribers.remove(q)

    def finalize(self,):
        """ Do not allow any more subscribers.

        Only used for memory efficiency if backlog is used.
        """
        log.debug("%s finalizing" % str(self))

        self.final = True
        if not self.backlog_use:
            return
        self.backlog = None

