import logging
from datetime import datetime

class Event:
    """
    A base class for all events that we can receive from targets
    """
    def __init__(self, data: dict = None, flopz_config: dict = None):
        """
        :param data: free-form dictionary, for example containing dumped registers or memory
        :param flopz_config: optionally, pass the flopz config down to this event for logging additional data
        """
        self.timestamp = datetime.now()
        self.type = ''
        if data:
            self.data = data
        else:
            self.data = {}
        self.flopz_config = flopz_config

    def is_interactive(self) -> bool:
        """
        Events can be interactive or non-interactive.
        :return: True, if this event requires interaction, False otherwise
        """
        return False

    def enter(self):
        """
        Interactive events will be 'entered'
        During enter(), the event takes over control and only returns when the event has been dealt with.
        Override this for interactive events.
        :return:
        """
        pass

    def pretty_print(self) -> str:
        """
        used for logging this event to a text string
        :return: a pretty-printed string
        """
        data_statements = [f"{k}: {v}" for k, v in self.data.items()]
        return f"Event: {self.type}, data: [{', '.join(data_statements)}]"

    def pretty_print_logger(self, logger: logging.Logger, level):
        """
        used for logging to the console or standard log files
        :param logger: a logging.Logger
        :return: nothing
        """
        logger.log(level, self.pretty_print())

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

