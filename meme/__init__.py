# Patch p4p close with Python 2.7
# For more details see: https://github.com/mdavidsaver/p4p/issues/55
from p4p.client import thread

_p4p_thread_context_close = thread.Context.close

def close(*args, **kwargs):
    try:
        _p4p_thread_context_close(*args, **kwargs)
    except TypeError:
        pass

thread.Context.close = close

from . import names
from . import archive
