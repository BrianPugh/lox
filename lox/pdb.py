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

class _Pdb(pdb.Pdb):
    def preloop(self):
        _pdb_lock.acquire()
        return super().preloop()

    def postloop(self):
        _pdb_lock.release()
        return super().postloop()

def set_trace(*, header=None):
    debugger = _Pdb()
    if header is not None:
        debugger.message(header)
    # maybe take lock here?
    debugger.set_trace(sys._getframe().f_back)
