"""
.. module:: announcement
   :synopsis: Queue elements for multiple recipients.
"""


import queue
from collections import deque

__all__ = ["Announcement",]

class Announcement:
    """ Put to many queues.
    """

    def __init__(self, maxsize=0):
        """

        Parameters
        ----------
        maxsize : int
            Created queue's maximum size. Defaults to 0 (no size limit)

        """

        self.subscribers = deque()
        self.maxsize = maxsize

    def __len__(self,):
        """ Get the number of subscribers.

        Returns
        -------
        int
            Number of subcribers.
        """

        return len(self.subscribers)

    def put(self, data, *args, **kwargs):
        """ Put data on all queues

        Parameters
        ----------
        data : object
            Data to put on the queue
        """

        for q in self.subscribers:
            q.put(data, *args, **kwargs)

    def subscribe(self, q=None, maxsize=None):
        """ Subscribe to announcements

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
            Queue-like object.
        """

        if q is None:
            if maxsize is None:
                maxsize = self.maxsize
            q = queue.Queue( maxsize=maxsize )
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q):
        """ Remove the queue from queue-list. Will no longer receive announcements

        Parameters
        ----------
        q : Queue
            Queue object to remove

        Raises
        ------
        ValueError
            ``q`` was not a subscriber.
        """

        self.subscribers.remove(q)
