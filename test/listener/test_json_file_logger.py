import argparse

from flopz.listener.event import Event
from flopz.listener.events.function_trace_event import FunctionTraceType, FunctionTraceEvent
from flopz.listener.loggers.json_file_logger import JsonFileLogger, JsonFileLoggerException
from util import working_directory
import json
import pytest
import os.path


def test_invalid_output_dir():
    with pytest.raises(JsonFileLoggerException):
        args = argparse.Namespace() # empty
        args.output_directory = None
        JsonFileLogger({}, args)

def test_logging_base_events(working_directory):
    ev = Event({"foo": "bar", "num": 1})
    ev.type = 'example_event'

    args = argparse.Namespace() # empty
    args.output_directory = working_directory
    logger = JsonFileLogger({}, args)

    # it should write to a timestamped file in working_directory
    assert(len(logger.logfile_name) > 0)
    assert(logger.logfile_name[-5:] == '.json')
    full_log_path = os.path.join(working_directory, logger.logfile_name)
    assert(os.path.isfile(full_log_path))

    # after logging has finished, the file should contain valid json
    logger.log(ev)
    logger.log(ev)
    logger.flush()
    logger.close()

    with open(full_log_path, 'r') as f:
        obj = json.load(f)
        assert(len(obj) == 2)
        assert(obj[0]['type'] == 'example_event')
        assert(obj[0]['type'] == 'example_event')
        assert(obj[0]['data']['foo'] == 'bar')
