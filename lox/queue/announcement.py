"""
.. module:: Announcement
   :synopsis: Many-to-many queue recipients with backlog support for
              race condition subscribing or lazy subscribing.
"""


import logging as log
import queue
import threading
from collections import deque

__all__ = [
    "Announcement",
    "SubscribeFinalizedError",
]


class SubscribeFinalizedError(Exception):
    """Raised when an Announcement.subscribe has been called,
    but the Announcement has already been finalized.
    """


class Announcement:
    """Push to many queues with backlog support.

    Allows the pushing of data to many threads.

    Example
    -------
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
        ...
        >>>
        >>> @lox.thread
        ... def bar():
        ...     x = bar_q.get()
        ...     return x**2
        ...
        >>>
        >>> ann.put(5)
        >>> foo.scatter()
        >>> foo_res = foo.gather()
        >>> bar.scatter()
        >>> bar_res = bar.gather()

    The backlog allows future (or potentially race-condition) subscribers to
    get content put'd before they subscribed. However, the user must be careful
    of memory consumption.
    """

    @property
    def final(
        self,
    ):
        return self._final

    @final.setter
    def final(self, val: bool):
        with self.lock:
            self._final = val

    @property
    def backlog(
        self,
    ):
        """collections.deque: Backlog of queued data. None if not used."""

        return self._backlog

    @backlog.setter
    def backlog(self, val):
        self._backlog = val

    def __repr__(
        self,
    ):
        with self.lock:
            qs = [str(id(ann.q)) for ann in self.subscribers]
            string = super().__repr__() + " with subscriber queues " + ",".join(qs)
        return string

    def __init__(self, maxsize=0, backlog=None):
        """Create an Announcement object.

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
        self.q = queue.Queue(maxsize=self.maxsize)
        self.subscribers.append(self)

        # Backlog objects #
        self.backlog_use = False if backlog is None else True
        self.final = False
        if self.backlog_use:
            if backlog <= 0:
                backlog = None
            self.backlog = deque(maxlen=backlog)
        else:
            self.backlog = None

    @classmethod
    def clone(cls, ann, q: queue.Queue = None):
        """Create a new announcement object that shares subscribers and resources
        with an existing announcement.

        Only difference from cloned announcement is a new receive queue is created.

        Parameters
        ----------
        ann : lox.Announcement
            Announcement object to clone from

        q : queue.Queue
            Receiving queue. If ``None``, a new one is created.

        Returns
        -------
        Announcement
           New Announcement object with copied attributes, but new ``q``
        """

        new_ann = cls()
        new_ann.lock = ann.lock
        with new_ann.lock:
            new_ann.subscribers = ann.subscribers
            new_ann.maxsize = ann.maxsize
            new_ann.q = queue.Queue(maxsize=ann.maxsize) if q is None else q
            new_ann.backlog_use = ann.backlog_use
            new_ann.backlog = ann.backlog
        return new_ann

    def __len__(
        self,
    ):
        """Get the number of subscribers.

        Returns
        -------
        int
            Number of subcribers.
        """

        return len(self.subscribers)

    def qsize(
        self,
    ):
        """Return the approximate size of the receive queue. Note, qsize() > 0
        doesn’t guarantee that a subsequent get() will not block, nor will
        qsize() < maxsize guarantee that put() will not block.

        Returns
        -------
        int
            approximate size of the receive queue.
        """

        return self.q.qsize()

    def empty(
        self,
    ):
        """Return ``True`` if the receive queue is empty, ``False`` otherwise.
        If ``empty()`` returns ``True`` it doesn’t guarantee that a subsequent
        call to ``put()`` will not block. Similarly, if ``empty()`` returns
        ``False`` it doesn’t guarantee that a subsequent call to ``get()``
        will not block.

        Returns
        -------
        bool
            ``True`` if the receive queue is currently empty; ``False`` otherwise.
        """

        return self.q.empty()

    def full(
        self,
    ):
        """Return ``True`` if the receive queue is full, ``False`` otherwise.
        If ``full()`` returns ``True`` it doesn’t guarantee that a subsequent
        call to ``get()`` will not block. Similarly, if ``full()`` returns
        ``False`` it doesn’t guarantee that a subsequent call to ``put()``
        will not block.

        Returns
        -------
        bool
            ``True`` if the receive queue is currently full; ``False`` otherwise.
        """

        return self.q.full()

    def put(
        self,
        item,
        block=True,
        timeout=None,
    ):
        """Put item into all subscribers' queues.

        Parameters
        ----------
        item
           data to put onto all subscribers' queues

        block : bool
            Block until data is put on queues or timeout.

        timeout : float
            Wait up to ``timeout`` seconds before raising ``queue.Full``.
            Defaults to no timeout.
        """

        with self.lock:
            for ann in self.subscribers:
                if ann == self:
                    log.debug("Skipping receiver Announcement %s" % ann)
                    continue
                else:
                    log.debug("Putting to Announcement %s" % str(ann))

                ann.q.put(item, block=block, timeout=timeout)
            if self.backlog_use and not self.final:
                self.backlog.append(item)

    def get(self, block=True, timeout=None):
        """Get from the receive queue.

        Parameters
        ----------
        block : bool
            Block until data is obtained from receive queue or timeout.

        timeout : float
            Wait up to ``timeout`` seconds before raising ``queue.Full``.
            Defaults to no timeout.

        Returns
        -------
            item from receive queue.

        Raises
        ------
        queue.Empty
             When there are no elements in queue and timeout has been reached.
        """

        return self.q.get(block=block, timeout=timeout)

    def subscribe(self, q=None, maxsize=None, block=True, timeout=None):
        """Subscribe to announcements.

        Parameters
        ----------
        q : Queue
            Existing queue to add to the subscribers' list.
            If not provided, a queue is created.

        maxsize : int
            Created queue's maximum size. Overrides Announcement's default
            maximum size. Ignored if ``q`` is provided.

        block : bool
            Block until data from backlog is put on queues or timeout.

        timeout : float
            Wait up to ``timeout`` seconds before raising ``queue.Full``.
            Defaults to no timeout.

        Returns
        -------
        Announcement
            object for receiver to ``get`` and ``put`` data from.
        """

        with self.lock:
            if self.final:
                log.error("%s Subscribe when announcement already finalized" % (self,))
                raise SubscribeFinalizedError

            if q is None:
                # Create Queue
                if maxsize is None:
                    maxsize = self.maxsize
                q = queue.Queue(maxsize=maxsize)
            ann = Announcement.clone(self, q)
            self.subscribers.append(ann)
            if self.backlog_use:
                for x in self.backlog:
                    q.put(x, block=block, timeout=timeout)
        return ann

    def unsubscribe(self, q):
        """Remove the queue from queue-list. Will no longer receive announcements.

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

    def finalize(
        self,
    ):
        """Do not allow any more subscribers.

        Primarily used for memory efficiency if backlog is used.
        """

        with self.lock:
            for ann in self.subscribers:
                log.debug("%s finalizing" % str(ann))
                ann.final = True
                ann.backlog = None
