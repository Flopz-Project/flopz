import argparse
from unittest.mock import MagicMock

from flopz.listener.event import Event
from flopz.listener.flopz_logger import FlopzLogger
from flopz.listener.loggers.console_logger import ConsoleLogger
from flopz.listener.loggers.chrome_trace_logger import ChromeTraceLogger

def test_base_logger():
    # all loggers have a reference to the (flopz) config and an optional logger config
    args = argparse.Namespace()
    l = FlopzLogger({}, args)
    assert(l.flopz_config is not None)
    assert(l.args == args)



def test_console_logger():
    # the logger pretty-prints each event to the console
    cl = ConsoleLogger({}, {})
    e = Event()
    e.pretty_print = MagicMock()
    cl.log(e)
    assert e.pretty_print.called
