import threading
from lox import OneWriterManyReader
from copy import copy
from time import sleep, time

SLEEP_TIME = 0.01
N_WORKERS = 5

rw_lock = None
resp_lock = None
resource = None

def common_setup():
    global rw_lock, resp_lock
    rw_lock = OneWriterManyReader()
    resp_lock = threading.Lock()

def common_create_workers(func, n, *args):
    threads = []
    for i in range(n):
        t = threading.Thread(target=func, args=args)
        t.setDaemon(True)
        threads.append(t)

    t_start = time()
    for t in threads:
        t.start()

    return threads, t_start

def read_worker():
    global resp_lock, rw_lock
    with rw_lock('r'):
        local_copy = copy(resource)
        sleep(SLEEP_TIME) # to make sure that all workers are truley accessing the resource at the same time

        # read resource
    with resp_lock:
        resp.append(local_copy)
    return

def write_worker(val):
    global rw_lock, resource
    with rw_lock('w'):
        print("meow "*10 + str(val))
        resource = val
    return

def test_OneWriterManyReader_r():
    global rw_lock, resp_lock, resource
    common_setup()
    resource = 0
    resp = []

    threads, t_start = common_create_workers(read_worker, N_WORKERS)
    for t in threads:
        t.join()
    t_end = time()
    t_diff = t_end-t_start

    assert( N_WORKERS > 2 )
    assert(t_diff < (N_WORKERS-1)*SLEEP_TIME) # for this to be true, readers have to access at same time (good)
    with resp_lock:
        for s in resp:
            assert(resp == resource)

def test_OneWriterManyReader_w():
    global rw_lock, resp_lock, resource
    common_setup()
    resource = 0
    new_val = 5

    threads_w1, t_start_w1 = common_create_workers(write_worker, 1, new_val)

    for t in threads_w1:
        t.join()

    assert( resource == new_val )

def test_OneWriterManyReader_rw():
    global rw_lock, resp_lock, resource
    common_setup()
    return
    resource = 0
    resp = []
    soln = [0,]*N_WORKERS + [5,]*N_WORKERS

    threads_r1, t_start_r1 = common_create_workers(read_worker, N_WORKERS)
    threads_w1, t_start_w1 = common_create_workers(write_worker, N_WORKERS, 5)
    threads_r2, t_start_r2 = common_create_workers(read_worker, N_WORKERS)

    for t in threads_r1:
        t.join()
    for t in threads_w1:
        t.join()
    for t in threads_r2:
        t.join()

    with resp_lock:
        for r,s in zip(resp, soln):
            assert( r == s )

