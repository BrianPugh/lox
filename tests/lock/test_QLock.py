from threading import Lock, Thread
from lox import QLock
from time import time, sleep

SLEEP_TIME = 0.1

def test_1():
    res = ""
    sol = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    qlock = QLock()

    def worker( x ):
        with qlock:
            res += x

    threads = []
    for name in sol:
        t = Thread(target=worker, args=(name,))
        t.start()
        threads.append(t)
        sleep(SLEEP_TIME) # probably enough time for .acquire() to run

    # Wait for all threads to complete
    for t in threads:
        t.join()

    for r, s in zip(res, sol):
        assert( r == s )
