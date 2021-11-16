import enum
import argparse

class LinkState(enum.Enum):
    INITIALIZED = 1,
    RUNNING = 2,
    ERROR = 3

class Link:
    """
    Link implements receiving and sending data over a physical or networked connection to the target.
    """
    def __init__(self, flopz_config: dict, arg_parser: argparse.Namespace):
        self.flopz_config = flopz_config
        self.arg_parser = arg_parser
        self.state = LinkState.INITIALIZED

    def start(self) -> None:
        """
        A non-blocking call that tells the Link to start listening and sending.
        Once the link has been started, it is ready to be used.
        :return: nothing
        """
        self.state = LinkState.RUNNING

    def stop(self) -> None:
        """
        A non-blocking call that tells the Link to stop
        Note that only when 'state' != RUNNING, the link can be considered fully stopped.
        :return: nothing
        """
        self.state = LinkState.INITIALIZED

    def get(self) -> bytes:
        """
        Ideally, this is a non-blocking call that returns received data or an empty byte string
        :return: a (potentially incomplete) chunk of received bytes
        """
        return b''

    def put(self, payload: bytes) -> int:
        """
        Send data over the link
        :param payload: which data to send
        :return: the number of bytes written
        """
        return 0

    @staticmethod
    def add_argparse(parser: argparse.ArgumentParser):
        """
        Add a Link-specific argument group and arguments
        :param parser:
        :return: nothing
        """
        return

    @staticmethod
    def name() -> str:
        """
        override this to return a unique name for your link
        :return: a string containing a unique name for this link class
        """
        return ''