import lox
from lox.helper import term_colors


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
