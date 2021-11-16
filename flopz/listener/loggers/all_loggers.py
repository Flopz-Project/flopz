from flopz.listener.loggers.console_logger import ConsoleLogger
from flopz.listener.loggers.chrome_trace_logger import ChromeTraceLogger
from flopz.listener.loggers.json_file_logger import JsonFileLogger

_all_loggers = [
    ConsoleLogger,
    JsonFileLogger,
    ChromeTraceLogger,
]

def get_all_loggers():
    return _all_loggers

def get_logger_by_name(name: str):
    for l in _all_loggers:
        if l.name() == name:
            return l