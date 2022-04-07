# -*- coding: utf-8 -*-

"""
Easy multithreading for every project.
"""

__author__ = """Brian Pugh"""
__email__ = "bnp117@gmail.com"
__version__ = "0.11.0"

import lox.worker
from lox.worker.process import process
from lox.worker.thread import thread

from .debug import *
from .exceptions import *
from .lock import *
from .queue import *
