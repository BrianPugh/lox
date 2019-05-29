import lox
from time import sleep, time

SLEEP_TIME = 0.01
N_WORKERS = 2


def test_basic_args():
    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.process(N_WORKERS) # specifying maximum number of processes
    def worker_task(x,y):
        sleep(SLEEP_TIME)
        return x * y

    # Vanilla function execution still works
    assert( 10 == worker_task(2,5) )

    assert( len(worker_task) == 0 )
    print("test_process: %s" % (worker_task))

    for x,y in zip(in_x, in_y):
        worker_task.scatter(x,y)

    res = worker_task.gather()

    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y) == r )

def test_basic_noargs():
    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.process # maximum number of processes = # cores
    def worker_task(x,y):
        sleep(SLEEP_TIME)
        return x * y

    # Vanilla function execution still works
    assert( 10 == worker_task(2,5) )

    assert( len(worker_task) == 0 )
    print("test_process: %s" % (worker_task))

    for x,y in zip(in_x, in_y):
        worker_task.scatter(x,y)

    res = worker_task.gather()

    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y) == r )

