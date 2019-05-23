import threading
import lox
from time import time, sleep

SLEEP_TIME = 0.1

def check_valid(res, n_resource):
    """ Checks to make sure a given value doesn't show up with N_WORKERS
    """
    n = len(res)
    for i in range(0, n, n_resource):
        upper = i + n_resource
        if upper > n:
            upper = n
        for j in range(i+1,upper):
            assert( res[i] != res[j] )

def test_with_no_args_1():
    print("meow")
    resource_semaphore = lox.ResourceSemaphore( 1 )
    print("meow")
    resp = 0
    with resource_semaphore:
        resp = 1
    assert(resp == 1)

def test_multithread_with_args_1():
    resp_lock = threading.Lock()
    resp = []
    n_resource = 5
    resource_semaphore = lox.ResourceSemaphore( n_resource )

    def func():
        with resource_semaphore(None) as index:
            sleep(SLEEP_TIME)
            with resp_lock:
                resp.append(index)

    threads = [threading.Thread(target=func) for _ in range(20) ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    check_valid(resp, n_resource)

def test_multithread_with_no_args_1():
    resp_lock = threading.Lock()
    resp = []
    n_resource = 5
    resource_semaphore = lox.ResourceSemaphore( n_resource )

    def func():
        with resource_semaphore as index:
            sleep(SLEEP_TIME)
            with resp_lock:
                resp.append(index)

    threads = [threading.Thread(target=func) for _ in range(20) ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    check_valid(resp, n_resource)

def test_invalid_constructor():
    try:
        resource_semaphore = lox.ResourceSemaphore( 0 )
        assert(False)
    except ValueError:
        assert(True)

def test_timeout():
    resource_semaphore = lox.ResourceSemaphore( 1 )
