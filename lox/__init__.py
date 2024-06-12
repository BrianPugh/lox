# -*- coding: utf-8 -*-

"""
Easy multithreading for every project.
"""

__author__ = """Brian Pugh"""
__email__ = "bnp117@gmail.com"
__version__ = "0.12.0"

__all__ = [
    "Announcement",
    "Funnel",
    "FunnelPutError",
    "FunnelPutTopError",
    "IndexSemaphore",
    "LOX_DEBUG",
    "LightSwitch",
    "QLock",
    "RWLock",
    "SubscribeFinalizedError",
    "Timeout",
    "process",
    "thread",
]

import lox.worker
from lox.worker.process import process
from lox.worker.thread import thread

from .debug import LOX_DEBUG
from .exceptions import Timeout
from .lock import IndexSemaphore, LightSwitch, QLock, RWLock
from .queue import (
    Announcement,
    Funnel,
    FunnelPutError,
    FunnelPutTopError,
    SubscribeFinalizedError,
)
