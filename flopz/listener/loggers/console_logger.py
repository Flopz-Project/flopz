import argparse
import logging

from flopz.listener.event import Event
from flopz.listener.flopz_logger import FlopzLogger

class ConsoleLogger(FlopzLogger):
    def __init__(self, flopz_config: dict, args: argparse.Namespace = None):
        super().__init__(flopz_config, args)
        self.logger = logging.getLogger('console_logger')
        # create logger
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s # %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def log(self, event: Event) -> None:
        self.logger.info(event.timestamp.isoformat() + " | " + event.pretty_print())

    @staticmethod
    def name() -> str:
        return 'console'

