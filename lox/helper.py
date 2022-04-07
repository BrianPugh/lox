"""
.. module:: helper
   :synopsis: Private general lox helper functions/classes
"""

__all__ = [
    "term_colors",
]


class term_colors:
    """Escape sequences to colorize text in the terminal"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __init__(self, color: str):
        self.color = color.lower()

    def __enter__(
        self,
    ):
        if self.color == "red":
            print(self.RED, end="")
        elif self.color == "green":
            print(self.GREEN, end="")
        elif self.color == "blue":
            print(self.BLUE, end="")
        elif self.color == "orange" or self.color == "yellow":
            print(self.ORANGE, end="")
        elif self.color == "bold":
            print(self.BOLD, end="")
        elif self.color == "underline":
            print(self.UNDERLINE, end="")
        elif self.color == "header":
            print(self.HEADER, end="")
        else:
            raise ValueError("Invalid color string")

    def __exit__(self, type, value, traceback):
        print(self.ENDC, end="", flush=True)
