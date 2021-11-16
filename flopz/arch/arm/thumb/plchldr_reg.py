from flopz.arch.register import Register

import enum


class PlchldrRegisterType(enum.IntEnum):
    GENERAL_PURPOSE = 0


class PlchldrRegister(Register):
    def __init__(self, name: str, val: int, reg_type: enum.IntEnum = None):
        super(PlchldrRegister, self).__init__(name=f"r{name}", val=val, reg_type=PlchldrRegisterType.GENERAL_PURPOSE)