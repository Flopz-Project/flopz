"""
higher-level arch for IA-32 processors
"""

from flopz.arch.architecture import Architecture
from flopz.arch.riscv.registers import RiscvRegister

import enum


class RiscvRegType(enum.IntEnum):
    GENERAL_PURPOSE = 0
    PROGRAM_COUNTER = 1
    ZERO_REGISTER = 2


class RiscvGenericArchitecture(Architecture):


    def __init__(self, register_class=RiscvRegister, reg_count=32):
        super().__init__(register_class=register_class)

        for i in range(1, reg_count):
            self.set_register(RiscvRegister(f"x{i}", i, RiscvRegType.GENERAL_PURPOSE))
        self.set_register(RiscvRegister("x0", 0, RiscvRegType.ZERO_REGISTER))

        # set a subset of CSRs
        self.mstatus = 0x300
        self.sstatus = 0x100
        self.mtvec = 0x303
        self.stvec = 0x105
        self.medeleg = 0x302
        self.mideleg = 0x303
        self.mip = 0x344
        self.mie = 0x304
        self.sip = 0x144
        self.sie = 0x104

    def set_register(self, reg):
        __name_map = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1',
                      'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11',
                      't3', 't4', 't5', 't6']

        setattr(self, reg.name, reg)
        setattr(self, __name_map[reg.val], reg)
        self.registers.append(reg)
