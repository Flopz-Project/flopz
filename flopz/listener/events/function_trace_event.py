import enum
import logging

from flopz.listener.event import Event

class FunctionTraceType(enum.Enum):
    FUNCTION_ENTRY = 0,
    FUNCTION_EXIT = 1

class FunctionTraceEvent(Event):
    def __init__(self, id: int, trace_type: FunctionTraceType, data: dict = None, flopz_config: dict = None):
        super().__init__(data, flopz_config)
        self.trace_type = trace_type
        self.id = id
        self.address = -1

        # try to extract address from flopz_config
        if flopz_config:
            if not 'gadgets' in flopz_config.keys():
                raise Exception("Invalid Flopz Config!")

            for gadget in flopz_config["gadgets"]:
                if not "trace" in gadget.keys():
                    continue

                if gadget["trace"]["id"] == self.id:
                    self.address = int(gadget["patch"]["addr"], 16)
                    self['address'] = self.address

    def pretty_print(self) -> str:
        return f"Function Trace Event: {self.trace_type.name} @ {hex(self.address)}"