from flopz.arch.register import Register

import enum

class VleRegisterType(enum.IntEnum):
    # see E200Z0.pdf
    GENERAL_PURPOSE = 0
    EXCEPTION_HANDLING_AND_CONTROL = 1
    PROCESSOR_CONTROL = 2
    DEBUG = 3
    MEMORY_MANAGEMENT = 4
    CACHE = 5


class VleGpRegister(Register):
    def __init__(self, name: str, val: int, reg_type: enum.IntEnum = None):
        super(VleGpRegister, self).__init__(name=f"r{name}", val=val, reg_type=VleRegisterType.GENERAL_PURPOSE)
