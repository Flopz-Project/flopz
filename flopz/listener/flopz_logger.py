import argparse

from flopz.listener.event import Event

class FlopzLogger:
    """
    A base class which handles logging events.
    """
    def __init__(self, flopz_config: dict, args: argparse.Namespace = None):
        self.flopz_config = flopz_config
        self.args = args

    def log(self, event: Event) -> None:
        """
        logs a single event
        :param event: the event to log
        :return: nothing
        """
        pass

    def flush(self):
        """
        Ensures that all data is written, f.ex. when logging to a file or socket
        """
        pass

    def close(self):
        """
        called before the program exits. close file handles etc.
        """
        pass

    @staticmethod
    def name() -> str:
        """
        :return: a unique name for this logger class
        """
        return ''