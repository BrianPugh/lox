from threading import Lock, Thread
from lox import IndexSemaphore
from time import time, sleep

SLEEP_TIME = 0.1

def test_with_no_args_1():
    resource_semaphore = IndexSemaphore( 1 )
    resp = 0
    with resource_semaphore:
        resp = 1
    assert(resp == 1)

def test_multithread_with_args_1():
    resp_lock = Lock()
    resp = []
    n_resource = 5
    resource_semaphore = IndexSemaphore( n_resource )
    locks = [Lock() for _ in range(n_resource)]

    def func():
        global locks
        with resource_semaphore as index:
            assert(locks[index].acquire(timeout=0))
            sleep(SLEEP_TIME)
            with resp_lock:
                resp.append(index)
            locks[index].release

    threads = [Thread(target=func) for _ in range(20) ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

def test_multithread_with_no_args_1():
    resp_lock = Lock()
    resp = []
    n_resource = 5
    resource_semaphore = IndexSemaphore( n_resource )
    locks = [Lock() for _ in range(n_resource)]

    def func():
        global locks
        with resource_semaphore as index:
            assert(locks[index].acquire(timeout=0))
            sleep(SLEEP_TIME)
            with resp_lock:
                resp.append(index)
            locks[index].release

    threads = [Thread(target=func) for _ in range(20) ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

def test_invalid_constructor():
    try:
        resource_semaphore = IndexSemaphore( 0 )
        assert False
    except ValueError:
        assert True

def test_timeout():
    resource_semaphore = IndexSemaphore( 1 )
    with resource_semaphore(timeout=None) as index1:
        assert( index1 == 0 )
        with resource_semaphore(timeout=0.1) as index2:
           assert index2 is None

