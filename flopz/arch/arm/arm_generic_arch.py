"""
higher-level arch for arm processors
"""

from flopz.arch.architecture import Architecture
from flopz.arch.register import Register

import enum


class ARMGenericRegisterType(enum.IntEnum):
    GENERAL_PURPOSE = 1


class ARMGenericArchitecture(Architecture):
    def __init__(self, register_class=Register):
        super(ARMGenericArchitecture, self).__init__(register_class=register_class)
        # initialize general-purpose registers
        for i in range(0, 16):
            setattr(self, f"r{i}", register_class(name=f"r{i}", val=i, reg_type=ARMGenericRegisterType.GENERAL_PURPOSE))

        self.registers = [getattr(self, f"r{i}") for i in range(0, 16)]

