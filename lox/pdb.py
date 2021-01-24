"""
For now, this file only supports multithreading.
"""

import sys
import threading
from functools import partial

import pdb
try:
    import ipdb
except ImportError:
    ipdb = None

_pdb_lock = threading.Lock()
_in_session = False


###################
# Internal Common #
###################

_super_set_continue = None
_super_set_quit = None
_super_set_trace = None


def _set_continue(self):
    global _in_session
    _in_session = False
    _pdb_lock.release()
    if _super_set_continue:
        return _super_set_continue()
    else:
        return super(type(self), self).set_continue()


def _set_quit(self):
    global _in_session
    _in_session = False
    _pdb_lock.release()
    if _super_set_quit:
        return _super_set_quit()
    else:
        return super(type(self), self).set_quit()


def _set_trace(self, frame=None):
    print(f"1frame: {frame}")
    global _in_session
    if not _in_session:
        _pdb_lock.acquire()
    _in_session = True

    if _super_set_trace:
        print(f"2frame: {frame}")
        return _super_set_trace(frame)
    else:
        return super(type(self), self).set_trace(frame)

#######
# PDB #
#######


class _Pdb(pdb.Pdb):
    def __init__(self, completekey='tab', stdin=None, stdout=None, skip=None,
                 nosigint=False, readrc=True):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout, skip=skip,
                         nosigint=nosigint, readrc=readrc)
        self.prompt = '(LoxPdb) '

    set_continue = _set_continue
    set_quit = _set_quit
    set_trace = _set_trace


def _pdb_set_trace(*, header=None):
    debugger = _Pdb()
    if header is not None:
        debugger.message(header)
    debugger.set_trace(sys._getframe().f_back.f_back)


########
# iPDB #
########

def _ipdb_set_trace(frame=None, context=None, cond=True):
    if not cond:
        return
    ipdb.__main__.wrap_sys_excepthook()
    if frame is None:
        frame = sys._getframe().f_back.f_back
    debugger_cls = ipdb.__main__._init_pdb(context)

    # Here we're monkeypatching the debugger, which is obviously bad practice,
    # but I haven't really investigated the inner workings of iPython
    global _super_set_continue
    global _super_set_quit
    global _super_set_trace
    _super_set_continue = debugger_cls.set_continue
    _super_set_quit = debugger_cls.set_quit
    _super_set_trace = debugger_cls.set_trace

    debugger_cls.set_continue = partial(_set_continue, debugger_cls)
    debugger_cls.set_quit = partial(_set_quit, debugger_cls)
    debugger_cls.set_trace = partial(_set_trace, debugger_cls)

    p = debugger_cls.set_trace(frame=frame)

    if p and hasattr(p, 'shell'):
        p.shell.restore_sys_module_state()

##########
# Common #
##########


def set_trace(**kwargs):
    if ipdb is not None:
        return _ipdb_set_trace(**kwargs)

    return _pdb_set_trace(**kwargs)
