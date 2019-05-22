import threading
from lox import LightSwitch
from copy import copy
from time import sleep, time

SLEEP_TIME = 0.01
N_WORKERS = 5

common_lock = None
counting_lock = None
resp_lock = None
resource = None

def common_setup():
    global common_lock, counting_lock, resp_lock

    common_lock = threading.Lock()
    counting_lock = LightSwitch(common_lock)
    resp_lock = threading.Lock()

def test_LightSwitch_1():
    global common_lock, counting_lock, resp_lock, resource
    common_setup()

    with counting_lock:
        acquired_lock = common_lock.acquire(timeout=0)
        assert(acquired_lock == False)
    acquired_lock = common_lock.acquire(timeout=0)
    assert(acquired_lock == True)
    common_lock.release()

def test_LightSwitch_len():
    global common_lock, counting_lock, resp_lock, resource
    common_setup()
    assert( 0==len(counting_lock) )
    counting_lock.acquire()
    assert( 1==len(counting_lock) )
    counting_lock.acquire()
    assert( 2==len(counting_lock) )
    counting_lock.release()
    assert( 1==len(counting_lock) )
    counting_lock.release()
    assert( 0==len(counting_lock) )

