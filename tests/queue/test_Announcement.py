import lox
from threading import Lock, Thread
from time import sleep
import queue

def test_1():
    ann = lox.Announcement()
    x_in = [1,2,3,4,5]
    foo_soln, bar_soln = [], []

    foo_q = ann.subscribe()
    bar_q = ann.subscribe()

    assert(isinstance(foo_q, queue.Queue))
    assert(isinstance(bar_q, queue.Queue))
    assert( foo_q != bar_q )

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

    assert( len(foo_soln) == len(x_in) )
    assert( len(bar_soln) == len(x_in) )

    for x, r in zip(x_in, foo_soln):
        assert( r == x**2)

    for x, r in zip(x_in, bar_soln):
        assert( r == x**3)

