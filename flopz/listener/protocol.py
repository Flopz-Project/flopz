from queue import Queue

from flopz.listener.event import Event
from flopz.listener.link import Link

class Protocol:
    """
    A base class for (wire) protocols that a target can implement.
    Protocols are used to interpret the data we receive over a link.
    Likewise, it can be used to encode data that we send to the target.
    A target can implement its own protocol or use a generic protocol.
    """
    def __init__(self, config: dict, link: Link):
        self.config = config
        self.events = Queue()

    def feed(self, data: bytes):
        """
        Consume a (potentially incomplete) chunk of bytes
        Generates events internally, as data comes in
        After calling this, you can check if events are available using has_events()
        :param data:
        """
        pass

    def has_events(self) -> bool:
        return self.events.qsize() > 0

    def get_event(self) -> Event:
        return self.events.get()

