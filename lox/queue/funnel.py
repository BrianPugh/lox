"""
.. module:: funnel
   :synopsis: Wait on many queues.

Wait on a queue until a set of inputs are ready.

Example usecase:
    Lets say 2 parallel algorithms:
        1. AlgoX computes the square of a number ``n``.
        2. AlgoY computes the squareroot of a number ``n``.
    Finally, lets say a third algorithm computes the sum:
        3. AlgoZ computes AlgoX + AlgoY
    AlgoX and AlgoY can be performed in parallel; however, AlgoZ requires a 
    pair of inputs to perform its computation. AlgoX and AlgoY could put their 
    results on a queue as they complete their tasks, but it's complicated for 
    AlgoZ to ``get`` a pair of matched items from both queues. **Funnel** 
    allows AlgoZ to easily wait on and ``get`` a pair from the 2 queues.
"""


import queue
from collections import deque
import threading
import logging as log

__all__ = ["Funnel", "FunnelPut",]

class FunnelPut(Exception):
    """ Cannot ``put`` to a top/master Funnel object;
    can only ``put`` to subscribers.
    """

    pass

class FunnelPutTop(Exception):
    pass

class FunnelElement:

    def __init__(self, item=None, complete=False):
        """
        Parameters
        ----------
        item
            User data
        complete : bool
            True if item contains valid data. 
        """

        self.item = item
        self.complete = complete

    def set(self, item):
        self.item = item
        self.complete = True


class Funnel:
    """ Wait on many queues.
    """

    def __init__(self):
        """ Create a Funnel Object
        """

        self.lock = threading.RLock()
        self.index = -1 # Index into list of solutions
        self.subscribers = deque()
        self.d = {}
        self.q = queue.Queue()          # Object that complete sets are placed on.

    @classmethod
    def _clone(cls, funnel):
        """ Create a new ``Funnel`` object that shares subscribers and resources
        with an existing ``Funnel``.

        Only difference is it's index is 1 higher than the funnel's last subscriber.

        Parameters
        ----------
        funnel : lox.Funnel
            ``Funnel`` object to clone from

        Returns
        -------
        Funnel
           New Funnel object.
        """

        new_funnel = cls()
        new_funnel.lock = funnel.lock 

        with new_funnel.lock:
            new_funnel.d = funnel.d
            new_funnel.q = funnel.q
            new_funnel.subscribers = funnel.subscribers
            new_funnel.index = len(funnel)
            log.debug("new_funnel.index == %d" % new_funnel.index)
            new_funnel.subscribers.append(new_funnel)

        return new_funnel

    def __len__(self,):
        """ Gets number of input queues.

        Returns
        -------
        int
            Number of input queues.
        """

        return len(self.subscribers)

    def subscribe(self,):
        """ Create a new Funnel for data to be ``put`` on. 

        Returns
        -------
        Funnel
            A funnel object that is a required input on ``get`` calls.
        """

        new_funnel = Funnel._clone(self)
        return new_funnel

    def put(self, item, jid, blocking=True, timeout=-1, ):
        """
        Parameters
        ----------
        item
           data to put onto all subscribers' queues

        jid : hashable
           unique identifier for job.

        block : bool
            Block until data is put on queues or timeout.

        timeout : float
            Wait up to ``timeout`` seconds before raising ``queue.Full``.
            Defaults to no timeout.

        Returns
        -------
        bool
            True if item was successfully added; False otherwise.

        Raises
        ------
        FunnelPutTop
           Can only put onto subscribers, not the top/master ``Funnel``.
        """

        if self.index < 0:
            raise FunnelPutTop

        if self.lock.acquire(blocking=blocking, timeout=timeout) == False:
            return False

        # put Item into dict's key's deque
        val = self.d.get(jid)
        if val is None:
            self.d[jid] = deque()

        for _ in range(len(self) - len(self.d[jid])):
            # Add a empty, incomplete funnel elements until it matches
            # the number of input queues.
            self.d[jid].append(FunnelElement())

        self.d[jid][self.index].set(item)

        # Add item to queue if all subscribers are accounted for.
        if all([elem.complete for elem in self.d[jid]]):
            log.debug("JID \"%s\" complete; putting onto queue %s" % (str(jid), str(self.q)))
            self.q.put(tuple([jid,] + [elem.item for elem in self.d[jid]]))
            del self.d[jid]

        self.lock.release()
        return True

    def get(self, block=True, timeout=None, return_jid=True):
        """ Get from the receive queue. Will return the contents of each 
        input queue in the order subscribed as a tuple

        Parameters
        ----------
        block : bool
            Block until data is obtained from receive queue or timeout.

        timeout : float
            Wait up to ``timeout`` seconds before raising ``queue.Full``.
            Defaults to no timeout.

        return_jid : bool
            Have the Job ID as the first element of the returned tuple.
            Defaults to True

        Returns
        -------
        tuple
            items from input queues.

        Raises
        ------
        queue.Empty
             When there are no elements in queue and timeout has been reached.
        """
        items = self.q.get(block=block, timeout=timeout)

        if return_jid:
            return items
        else:
            return items[1:]
