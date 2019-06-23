import lox
from lox.worker import ScatterPromise
from queue import Queue
from threading import Lock
from collections import deque
from time import sleep, time


SLEEP_TIME = 0.01

def test_ScatterPromise_1():
    val = 3
    queue = Queue()
    lock = Lock(); lock.acquire()

    sol_array = deque()
    for i in range(val+1):
        sol_array.append(None)

    sp = ScatterPromise(val, queue, lock, sol_array)

    t_start = time()
    try:
        sp.resolve(timeout=SLEEP_TIME)
        assert( False )
    except lox.Timeout:
        pass
    t_delta = abs(time()-t_start - SLEEP_TIME)
    assert( t_delta < 0.001)

