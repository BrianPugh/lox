from collections import deque
from threading import Lock, Thread
from time import sleep, time

import pytest

from lox import IndexSemaphore

SLEEP_TIME = 0.01
n_resource = 5
n_threads = 20


def test_multithread_args():
    resp = deque()
    sem = IndexSemaphore(n_resource)
    locks = [Lock() for _ in range(n_resource)]

    def func():
        nonlocal locks
        index = sem.acquire(timeout=100)
        if locks[index].acquire(timeout=0):
            # Acquired Test Lock with no waiting, indicating this index is unique
            sleep(SLEEP_TIME)
            locks[index].release()
            resp.append(True)
        else:
            # timeout (bad)
            resp.append(False)
        sem.release(index)

    threads = [Thread(target=func) for _ in range(n_threads)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for r in resp:
        assert r
    assert len(resp) == n_threads


def test_multithread_no_args():
    resp = deque()
    sem = IndexSemaphore(n_resource)
    locks = [Lock() for _ in range(n_resource)]

    def func():
        nonlocal locks
        index = sem.acquire()
        if locks[index].acquire(timeout=0):
            # Acquired Test Lock with no waiting, indicating this index is unique
            sleep(SLEEP_TIME)
            locks[index].release()
            resp.append(True)
        else:
            # timeout (bad)
            resp.append(False)
        sem.release(index)

    threads = [Thread(target=func) for _ in range(n_threads)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for r in resp:
        assert r
    assert len(resp) == n_threads


def test_multithread_context_args():
    resp = deque()
    sem = IndexSemaphore(n_resource)
    locks = [Lock() for _ in range(n_resource)]

    def func():
        nonlocal locks
        with sem(timeout=None) as index:
            if locks[index].acquire(timeout=0):
                # Acquired Test Lock with no waiting, indicating this index is unique
                sleep(SLEEP_TIME)
                locks[index].release()
                resp.append(True)
            else:
                # timeout (bad)
                resp.append(False)

    threads = [Thread(target=func) for _ in range(n_threads)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for r in resp:
        assert r
    assert len(resp) == n_threads


def test_multithread_context_no_args():
    resp = deque()
    sem = IndexSemaphore(n_resource)
    locks = [Lock() for _ in range(n_resource)]

    def func():
        nonlocal locks
        with sem() as index:
            if locks[index].acquire(timeout=0):
                # Acquired Test Lock with no waiting, indicating this index is unique
                sleep(SLEEP_TIME)
                locks[index].release()
                resp.append(True)
            else:
                # timeout (bad)
                resp.append(False)

    threads = [Thread(target=func) for _ in range(n_threads)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for r in resp:
        assert r
    assert len(resp) == n_threads


def test_invalid_constructor():
    with pytest.raises(ValueError):
        IndexSemaphore(0)


def test_timeout():
    sem = IndexSemaphore(1)
    with sem(timeout=None) as index1:
        assert index1 == 0
        with sem(timeout=0.1) as index2:
            assert index2 is None
