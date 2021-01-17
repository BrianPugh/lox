"""
For now, this file only supports multithreading.
"""

import sys
import threading

try:
    import ipdb as pdb
    raise ImportError  # TODO: ipdb support
except ImportError:
    import pdb

_pdb_lock = threading.Lock()
_in_session = False

class _Pdb(pdb.Pdb):
    def __init__(self, completekey='tab', stdin=None, stdout=None, skip=None,
                     nosigint=False, readrc=True):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout, skip=skip,
                     nosigint=nosigint, readrc=readrc)
        self.prompt = '(LoxPdb) '

    def set_continue(self):
        global _in_session
        _in_session = False
        _pdb_lock.release()
        super().set_continue()

    def set_quit(self):
        global _in_session
        _in_session = False
        _pdb_lock.release()
        super().set_quit()

    def set_trace(self, frame=None):
        global _in_session
        if not _in_session:
            _pdb_lock.acquire()
        _in_session = True
        res = super().set_trace(frame)
        return res

def set_trace(*, header=None):
    debugger = _Pdb()
    if header is not None:
        debugger.message(header)
    debugger.set_trace(sys._getframe().f_back)
