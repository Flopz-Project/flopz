import enum
import struct

from flopz.listener.events.function_trace_event import FunctionTraceEvent, FunctionTraceType
from flopz.listener.link import Link
from flopz.listener.protocol import Protocol
from flopz.listener.event import Event

class BoleroProtocolState(enum.Enum):
    EXPECT_FUNC_ID = 0,

class BoleroProtocol(Protocol):
    def __init__(self, config: dict, link: Link):
        super().__init__(config, link)
        self.state = BoleroProtocolState.EXPECT_FUNC_ID

    def feed(self, data: bytes):
        if len(data) > 1:
            can_id, length = struct.unpack('IB', data[:5])
            can_data = data[5:]
            if len(can_data) < 2:
                return b''  # too short
            data_idx = 0
            if can_id in range(0x7f0, 0x7ff):
                while data_idx < len(data):
                    if self.state == BoleroProtocolState.EXPECT_FUNC_ID:
                        # generate function trace event
                        # data should be an unsigned short, 16 bit
                        if len(can_data[data_idx:]) > 1:
                            func_id = struct.unpack('>H', can_data[data_idx:data_idx + 2])[0]
                            ev = FunctionTraceEvent(id=func_id, trace_type=FunctionTraceType.FUNCTION_ENTRY,
                                                    flopz_config=self.config)
                            self.events.put(ev)
                            data_idx += 2
                        else:
                            break
            else:
                return b''  # this frame is not for us

