from threading import Lock, Thread
from time import sleep, time

from lox import QLock

SLEEP_TIME = 0.1


def test_1():
    res = ""
    sol = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    qlock = QLock()

    def worker(x):
        nonlocal res
        with qlock:
            res += x

    threads = []
    for name in sol:
        t = Thread(target=worker, args=(name,))
        t.start()
        threads.append(t)
        sleep(SLEEP_TIME)  # probably enough time for .acquire() to run

    # Wait for all threads to complete
    for t in threads:
        t.join()

    for r, s in zip(res, sol):
        assert r == s


def test_timeout():
    qlock = QLock()
    assert qlock.acquire()
    assert qlock.acquire(timeout=SLEEP_TIME) is False


def test_perf_qlock(benchmark):
    lock = QLock()

    @benchmark
    def acquire_release():
        lock.acquire()
        lock.release()


def test_perf_lock(benchmark):
    lock = Lock()

    @benchmark
    def acquire_release():
        lock.acquire()
        lock.release()
