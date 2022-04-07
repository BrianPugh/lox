import os

_truelike = set(["true", "t", "yes", "y", "1"])
LOX_DEBUG = os.getenv("LOX_DEBUG", 'False').lower() in _truelike
