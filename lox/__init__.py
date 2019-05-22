# -*- coding: utf-8 -*-

"""Top-level package for lox."""

__author__ = """Brian Pugh"""
__email__ = 'bnp117@gmail.com'
__version__ = '0.1.0'

from lox.lock.LightSwitch import *
from lox.lock.OneWriterManyReader import *

# Take from other libraries for simplicity
from threading import Lock, Thread
from queue import Queue
