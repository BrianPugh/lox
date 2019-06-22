"""
.. module:: helper
   :synopsis: Private general lox helper functions/classes
"""


__all__ = ["auto_adapt_to_methods", "MethodDecoratorAdaptor", "term_colors"]

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
        return self.decorator(self.func)(*args, **kwargs)

    def __get__(self, instance, owner):
        return self.decorator(self.func.__get__(instance, owner))

    def __getattr__(self, attr):
        return getattr(self.decorator(self.func), attr)

    def __len__(self,):
        return len(self.decorator(self.func))

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
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
