import lox
from lox import Announcement
from threading import Lock, Thread
from time import sleep
import queue

def test_1():
    """ Test most basic usecase with 1 subscribers.
    """
    funnel = lox.Funnel()
    sub_1 = funnel.subscribe()

    sub_1.put('foo', 'job_id')
    res = funnel.get()
    assert(len(res) == 2)
    assert(res[0] == 'job_id')
    assert(res[1] == 'foo')
    assert(funnel.d == {})

def test_2():
    """ Test most basic usecase with 2 subscribers.
    """

    funnel = lox.Funnel()
    sub_1 = funnel.subscribe()
    sub_2 = funnel.subscribe()

    sub_1.put('foo', 'job_id')
    try:
        res = funnel.get(timeout=0.01)
        assert(0)
    except queue.Empty:
        assert(1)

    sub_2.put('bar', 'job_id')

    res = funnel.get()
    assert(len(res) == 3)
    assert(res[0] == 'job_id')
    assert(res[1] == 'foo')
    assert(res[2] == 'bar')
    assert(funnel.d == {})
