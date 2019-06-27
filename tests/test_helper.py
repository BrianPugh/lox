import lox
from lox.helper import term_colors, cdf, cdfi
from time import sleep, time
import sys, gc

SLEEP_TIME = 0.01

def test_ctx(capsys):
    with capsys.disabled():
        print("")
        with term_colors("red"):
            print("test red")
        with term_colors("green"):
            print("test green")
        with term_colors("blue"):
            print("test blue")
        with term_colors("orange"):
            print("test orange")
        with term_colors("underline"):
            print("test underline")
        with term_colors("bold"):
            print("test bold")
        with term_colors("header"):
            print("test header")


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

def test_MethodDecoratorAdaptor_gc():
    len_cdfi = len(cdfi)
    
    for i in range(100):
        obj = Class1(i)
        obj.test_method1.scatter(i,i+1)
        obj.test_method1.gather()
        del obj
    gc.collect()

    # cdfi should be as it previously was, otherwise gc isn't working
    assert(len_cdfi == len(cdfi))
