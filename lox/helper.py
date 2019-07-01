"""
.. module:: helper
   :synopsis: Private general lox helper functions/classes
"""

import sys
import gc


__all__ = ["auto_adapt_to_methods", "MethodDecoratorAdaptor", "term_colors",]

cdf = {} # cached (decorator, func)
cdfi = {} # cached (instance, owner, decorator, func)

def cdfi_gc_cb(phase, info):
    """ Garbage Collector callback to free deleted cdfi entries"""

    global cdfi
    if phase == "start":
        remove = [k for k,v in cdfi.items() if sys.getrefcount(v.func.__self__) <= 3]
        for k in remove: del cdfi[k]

gc.callbacks.append(cdfi_gc_cb)

class MethodDecoratorAdaptor:
    """ Class that allows the same decorator apply to methods and functions """

    def __init__(self, decorator, func):
        """
        Parameters
        ----------
        decorator : function
            Decorator function that takes in a single parameter, "func"
        func : function
            Function/Method that is being decorated
        """
        self.decorator = decorator
        self.func = func

    def __call__(self, *args, **kwargs):
        return self._get_cdf()(*args, **kwargs)

    def __get__(self, instance, owner):
        global cdfi
        k = (instance, owner, self.decorator, self.func)
        if k not in cdfi:
            cdfi[k] = self.decorator(self.func.__get__(instance, owner))
        return cdfi[k]

    def __getattr__(self, attr):
        return getattr(self._get_cdf(), attr)

    def __len__(self,):
        return len(self._get_cdf())

    def _get_cdf(self):
        global cdf
        k = (self.decorator, self.func)
        if k not in cdf:
            cdf[k] = self.decorator(self.func)
        return cdf[k]


def auto_adapt_to_methods(decorator):
    """Decorator that allows you to use the same decorator on methods and 
    functions, hiding the self argument from the decorator.
    
    Source: https://stackoverflow.com/a/1288936"""

    def adapt(func):
        return MethodDecoratorAdaptor(decorator, func)
    return adapt

class term_colors:
    """ Escape sequences to colorize text in the terminal """

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self, color:str):
        self.color = color.lower()

    def __enter__(self, ):
        if self.color == 'red':
            print(self.RED, end='')
        elif self.color == 'green':
            print(self.GREEN, end='')
        elif self.color == 'blue':
            print(self.BLUE, end='')
        elif self.color == 'orange' or self.color == 'yellow':
            print(self.ORANGE, end='')
        elif self.color == 'bold':
            print(self.BOLD, end='')
        elif self.color == 'underline':
            print(self.UNDERLINE, end='')
        elif self.color == 'header':
            print(self.HEADER, end='')
        else:
            raise ValueError("Invalid color string")

    def __exit__(self, type, value, traceback):
        print(self.ENDC, end='', flush=True)

