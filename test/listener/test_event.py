import logging
from datetime import datetime

from flopz.listener.event import Event
from util import DummyLogger


def test_event():
    # by default, events should not be interactive
    e = Event()
    assert(not e.is_interactive())

    # all events have a timestamp, created in their constructor
    assert(e.timestamp != None)

    # this timestamp should store the time that the event was created
    before_create = datetime.now()
    e = Event()
    after_create = datetime.now()
    assert(before_create <= e.timestamp)
    assert(e.timestamp <= after_create)

    # all events have a type string attribute that is empty by default
    assert(e.type == '')

    # all events accept an optional data parameter, containing a dictionary of keys and values describing the event
    e = Event({"foo": "bar"})
    assert(e.data is not None)

    # event data can be accessed using the __getitem__ operator
    assert(e['foo'] == 'bar')

    # ..and the __setitem__ operator
    e['test'] = 123
    assert(e['test'] == 123)

    # events should pretty print all their data
    e = Event({"foo": "bar"})
    logger = DummyLogger()
    e.pretty_print_logger(logger, 1)
    assert(logger.logged_value == 'Event: , data: [foo: bar]')
    assert(e.pretty_print() == 'Event: , data: [foo: bar]')

