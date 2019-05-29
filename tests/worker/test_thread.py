import threading
import lox
from time import sleep, time

SLEEP_TIME = 0.01
N_WORKERS = 5

def test_basic_args():
    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.thread(N_WORKERS) # specifying maximum number of threads
    def worker_task(x,y):
        sleep(SLEEP_TIME)
        return x * y

    # Vanilla function execution still works
    assert( 10 == worker_task(2,5) )

    assert( len(worker_task) == 0 )

    for x,y in zip(in_x, in_y):
        worker_task.scatter(x,y)
    res = worker_task.gather()

    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y) == r )

def test_basic_noargs():
    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.thread # defaults to a max of 50 threads if none specified
    def worker_task(x,y):
        sleep(SLEEP_TIME)
        return x * y

    # Vanilla function execution still works
    assert( 10 == worker_task(2,5) )

    assert( len(worker_task) == 0 )

    for x,y in zip(in_x, in_y):
        worker_task.scatter(x,y)
    res = worker_task.gather()

    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y) == r )

