import argparse

from flopz.listener.event import Event
from flopz.listener.flopz_logger import FlopzLogger
import os.path
import json
from datetime import datetime
import queue

class JsonFileLoggerException(Exception):
    pass

class JsonFileLogger(FlopzLogger):
    def __init__(self, flopz_config: dict, args: argparse.Namespace):
        super().__init__(flopz_config, args)
        if not args.output_directory:
            raise JsonFileLoggerException("No output path specified!")

        self.output_dir = args.output_directory
        if not os.path.exists(self.output_dir):
            raise JsonFileLoggerException("Output directory does not exist!")

        # holds a list of formatted objects that regularly get flushed into the json file
        self.output_objects = queue.Queue()

        self.log_time = datetime.now().strftime("%d-%m-%y_%M-%S")
        self.target_identifier = ''
        if 'project' in flopz_config.keys():
            self.target_identifier += flopz_config['project']
            if 'binary' in flopz_config.keys() and len(flopz_config['binary']) > 0:
                self.target_identifier += '_' + flopz_config['binary']

        # create a new log file and prepare it for writing
        self.logfile_name = self.log_time + '_' + self.target_identifier + '.json'
        self.logfile = open(os.path.join(self.output_dir, self.logfile_name), 'w')

        # directly using the json module has some downsides, so we make a compromise
        # the file is treated as a text file, but objects are encoded using the json module,
        # ..and streamed to the file whenever it makes sense
        self.logfile.write('[\n')
        self.write_first_entry = True

    def log(self, event: Event) -> None:
        json_obj = json.dumps({
            'type': event.type,
            'ts': event.timestamp.isoformat(), # will include microseconds
            'data': {
                **event.data
            }
        })
        self.output_objects.put(json_obj)
        if self.output_objects.qsize() > 20:
            self.flush()

    def flush(self):
        if self.logfile.closed:
            raise JsonFileLoggerException("File closed before flushing!")
            return

        while self.output_objects.qsize() > 0:
            obj = self.output_objects.get()
            if self.write_first_entry:
                self.logfile.write(obj)
                self.write_first_entry = False
            else:
                self.logfile.write(',' + '\n' + obj)

    def close(self):
        self.logfile.write('\n]')
        self.logfile.flush()
        self.logfile.close()

    @staticmethod
    def name() -> str:
        return 'json'

