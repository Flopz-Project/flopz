from flopz.arch.register import *


class RiscvRegister(Register):
    def __init__(self, name: str, val: int, reg_type: IntEnum):
        super().__init__(name, val, reg_type)