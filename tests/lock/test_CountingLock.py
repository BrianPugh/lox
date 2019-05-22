import threading
from lox import CountingLock
from copy import copy
from time import sleep, time

SLEEP_TIME = 1.5
N_WORKERS = 5

rw_lock = None
resp_lock = None
resource = None

def common_setup():
    global rw_lock, resp_lock
    rw_lock = OneWriterManyReader()
    resp_lock = threading.Lock()

def test_CountingLock_1():
    pass
