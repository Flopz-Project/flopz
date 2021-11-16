"""
higher-level arch for PPC processors
"""

from flopz.arch.architecture import Architecture
from flopz.arch.register import Register

import enum


class PPCGenericRegisterType(enum.IntEnum):
    GENERAL_PURPOSE = 1
    SPECIAL_PURPOSE = 2
    

class PPCGenericArchitecture(Architecture):
    def __init__(self, register_class=Register):
        super(PPCGenericArchitecture, self).__init__(register_class=register_class)
        # initialize general-purpose registers
        for i in range(0,32):
            setattr(self, f"r{i}", register_class(name=f"r{i}", val=i, reg_type=PPCGenericRegisterType.GENERAL_PURPOSE))
        self.registers = [getattr(self, f"r{i}") for i in range(0,32)]

        self.SPRG0 = register_class(name='SPRG0', val=272, reg_type=PPCGenericRegisterType.SPECIAL_PURPOSE)
        self.registers.append(self.SPRG0)