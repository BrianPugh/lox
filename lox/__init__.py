# -*- coding: utf-8 -*-

"""
Easy multithreading for every project.
"""

__author__ = """Brian Pugh"""
__email__ = 'bnp117@gmail.com'
__version__ = '0.10.0'

from .lock import *
from .queue import *
from .worker import *
from .exceptions import *

from lox.worker.thread import thread
from lox.worker.process import process
