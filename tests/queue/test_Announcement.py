import queue
from threading import Lock, Thread
from time import sleep

import pytest

import lox
from lox import Announcement


def test_1():
    """Test most basic usecase."""

    ann = lox.Announcement()
    x_in = [1, 2, 3, 4, 5]
    foo_soln, bar_soln = [], []

    foo_q = ann.subscribe()
    bar_q = ann.subscribe()

    assert isinstance(foo_q, lox.Announcement)
    assert isinstance(bar_q, lox.Announcement)
    assert foo_q != bar_q

    def foo():
        x = foo_q.get()
        foo_soln.append(x**2)

    def bar():
        x = bar_q.get()
        bar_soln.append(x**3)

    threads = []
    for _ in x_in:
        threads.append(Thread(target=foo))
        threads.append(Thread(target=bar))

    for x in x_in:
        ann.put(x)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert len(foo_soln) == len(x_in)
    assert len(bar_soln) == len(x_in)

    for x, r in zip(x_in, foo_soln):
        assert r == x**2

    for x, r in zip(x_in, bar_soln):
        assert r == x**3


def test_2():
    """Test the backlog."""

    ann = lox.Announcement(backlog=0)
    x_in = [1, 2, 3, 4, 5]
    foo_soln, bar_soln = [], []

    foo_q = ann.subscribe()

    def foo():
        x = foo_q.get()
        foo_soln.append(x**2)

    def bar():
        x = bar_q.get()
        bar_soln.append(x**3)

    threads = []
    for _ in x_in:
        threads.append(Thread(target=foo))
        threads.append(Thread(target=bar))

    for x in x_in:
        ann.put(x)

    bar_q = ann.subscribe()
    ann.finalize()

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert len(foo_soln) == len(x_in)
    assert len(bar_soln) == len(x_in)

    for x, r in zip(x_in, foo_soln):
        assert r == x**2

    for x, r in zip(x_in, bar_soln):
        assert r == x**3


def test_3():
    """Test subscribing after finalize."""

    ann = lox.Announcement()
    ann.finalize()
    with pytest.raises(lox.SubscribeFinalizedError):
        ann.subscribe()


def test_4():
    """Testing many-to-many capability."""

    ann_foo = Announcement()
    ann_bar = ann_foo.subscribe()
    ann_baz = ann_bar.subscribe()

    ann_foo.put(1)

    assert ann_bar.get() == 1
    assert ann_baz.get() == 1

    ann_bar.put(2)
    assert ann_foo.get() == 2
    assert ann_baz.get() == 2

    ann_bar.put(3)
    assert ann_foo.get() == 3
    assert ann_baz.get() == 3


def test_5():
    """Testing many-to-many backlog and finalization."""

    ann_foo = lox.Announcement(backlog=-1)
    ann_bar = ann_foo.subscribe()

    ann_foo.put(1)
    ann_foo.put(3)
    ann_foo.put(7)

    assert ann_bar.get() == 1
    assert ann_bar.get() == 3
    assert ann_bar.get() == 7

    ann_baz = ann_bar.subscribe()

    assert ann_baz.get() == 1
    assert ann_baz.get() == 3
    assert ann_baz.get() == 7

    ann_boo = ann_bar.subscribe()
    ann_boo.finalize()

    assert ann_boo.get() == 1
    assert ann_boo.get() == 3
    assert ann_boo.get() == 7

    with pytest.raises(queue.Empty):
        ann_boo.get(timeout=0.01)

    with pytest.raises(lox.SubscribeFinalizedError):
        ann_foo.subscribe()
