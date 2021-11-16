from flopz.listener.events.function_trace_event import FunctionTraceEvent, FunctionTraceType

from util import DummyLogger

def test_function_trace_event():
    ft = FunctionTraceEvent(1, FunctionTraceType.FUNCTION_ENTRY)

    # a function trace event should have an id
    assert(ft.id == 1)

    flopz_config = {
        "gadgets": [{
            "trace": {
                "id": 1,
                "level": "function",
                "dump": [
                    {
                        "type": "id"
                    }
                ]
            },
            "patch": {
                "addr": "0x1234"
            }
        }]
    }

    ft = FunctionTraceEvent(1, FunctionTraceType.FUNCTION_ENTRY, {}, flopz_config)
    # a function trace event should extract the associated address from the flopz config
    assert(ft.address == 0x1234)
    assert(ft['address'] == 0x1234)

    # it should include the address and function trace type in pretty_print
    logger = DummyLogger()
    ft.pretty_print_logger(logger, 1)
    assert(logger.logged_value == 'Function Trace Event: FUNCTION_ENTRY @ 0x1234')



