import threading
import lox
from time import sleep, time
import logging as log

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

    #assert( len(worker_task) == 0 )

    for x,y in zip(in_x, in_y):
        worker_task.scatter(x,y)
    res = worker_task.gather()

    assert(len(res) == len(in_x))

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

    assert(len(res) == len(in_x))

    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y) == r )

class Class1:

    def __init__(self, z):
        self.z = z

    @lox.thread(2)
    def test_method1(self, x, y):
        sleep(SLEEP_TIME)
        return x*y + self.z

    @lox.thread
    def test_method2(self, x, y):
        sleep(SLEEP_TIME)
        return x*y - self.z

def test_method_1():
    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]
    z1 = 5
    z2 = 5

    test_obj_1 = Class1( z1 )
    test_obj_2 = Class1( z2 )

    assert( (2*5+z1) == test_obj_1.test_method1(2,5) )
    assert( (2*5-z1) == test_obj_1.test_method2(2,5) )

    assert( (2*5+z2) == test_obj_2.test_method1(2,5) )
    assert( (2*5-z2) == test_obj_2.test_method2(2,5) )

    for i in range(2):
        for x,y in zip(in_x, in_y):
            test_obj_1.test_method1.scatter(x,y)
        res = test_obj_1.test_method1.gather()
        assert(len(res) == len(in_x))
        for r,x,y in zip(res, in_x, in_y):
            assert( (x*y+z1) == r )

    for x,y in zip(in_x, in_y):
        test_obj_2.test_method1.scatter(x,y)
    res = test_obj_2.test_method1.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y+z2) == r )


    for x,y in zip(in_x, in_y):
        test_obj_1.test_method2.scatter(x,y)
    res = test_obj_1.test_method2.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y-z1) == r )

    for x,y in zip(in_x, in_y):
        test_obj_2.test_method2.scatter(x,y)
    res = test_obj_2.test_method2.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( (x*y-z2) == r )

def test_chaining_1():
    """ Naive chaining with no additional arguments
    """

    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.thread(2)
    def foo(x,y):
        return x, x*y

    @lox.thread(2)
    def bar(x,y):
        return x + y

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y))
    res = bar.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( x+(x*y) == r )

    log.info("First chain call successful")

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(y,x))
    res = bar.gather() # Should internally call gather of all previous functions
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( y+(y*x) == r )

def test_chaining_1_1():
    """ Naive chaining when func doesn't return a tuple
    """

    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.thread(2)
    def foo(x,y):
        return x + y

    @lox.thread(2)
    def bar(x):
        return x ** 2

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y))
    res = bar.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( (x+y)**2 == r )

    log.info("First chain call successful")

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y))
    res = bar.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( (x+y)**2 == r )

def test_chaining_1_2():
    """ Naive chaining when func return a tuple without auto_unpacking.
    """

    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]

    @lox.thread(2)
    def foo(x,y):
        return x**2, y**2

    @lox.thread(2)
    def bar(x):
        return x[0] + x[1]

    bar.disable_auto_unpacking()

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y))
    res = bar.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( x**2+y**2 == r )

    log.info("First chain call successful")

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y))
    res = bar.gather()
    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( x**2+y**2 == r )

def test_chaining_2():
    """ Test positional arguments while chaining
    """

    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]
    z = 5

    @lox.thread(2)
    def foo(x,y):
        return x, x*y

    @lox.thread(2)
    def bar(x,y,z):
        return x + y + 2*z

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y), z)
    res = bar.gather()

    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( x+(x*y)+2*z == r )

    for x,y in zip(in_x, in_y):
        bar.scatter(z, foo.scatter(x,y))
    res = bar.gather()

    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( bar(z, *foo(x,y)) == r )

def test_chaining_3():
    """ Test kwargs arguments while chaining
    """

    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]
    z = 5

    @lox.thread(2)
    def foo(x,y):
        return x, x*y

    @lox.thread(2)
    def bar(x,y, dummy=0, z=-1):
        return x + y + 2*z

    for x,y in zip(in_x, in_y):
        bar.scatter(foo.scatter(x,y), z=z)
    res = bar.gather()

    assert(len(res) == len(in_x))
    for r,x,y in zip(res, in_x, in_y):
        assert( x+(x*y)+2*z == r )

def test_chaining_4():
    """ Test parallel chaining
    """

    in_x = [1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,]
    in_y = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,]
    z = 5

    @lox.thread(2)
    def foo(x,y):
        return x, x*y

    @lox.thread(2)
    def bar(x,y, dummy=0, z=-1):
        return x + y + 2*z

    @lox.thread(2)
    def baz(a,b):
        return a*b

    for x,y in zip(in_x, in_y):
        res1 = foo.scatter(x,y)
        res2 = bar.scatter(res1, z=z)
        res3 = baz.scatter(res1)
    bar_res = bar.gather()
    baz_res = baz.gather()

    assert( len(bar_res) == len(in_x) )
    assert( len(baz_res) == len(in_x) )

    for r,x,y in zip(bar_res, in_x, in_y):
        assert( bar(*foo(x,y), z=z) == r )
    for r,x,y in zip(baz_res, in_x, in_y):
        assert( baz(*foo(x,y)) == r )

