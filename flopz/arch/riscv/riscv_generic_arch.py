"""
higher-level arch for RiscV processors
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

        # set the 32 RiscV standard registers (use name and xNumber both)
        self.zero = RiscvRegister("zero", 0, RiscvRegType.ZERO_REGISTER)
        self.x0 = self.zero
        self.ra = RiscvRegister("ra", 1, RiscvRegType.GENERAL_PURPOSE)
        self.x1 = self.ra
        self.sp = RiscvRegister("sp", 2, RiscvRegType.GENERAL_PURPOSE)
        self.x2 = self.sp
        self.gp = RiscvRegister("gp", 3, RiscvRegType.GENERAL_PURPOSE)
        self.x3 = self.gp
        self.tp = RiscvRegister("tp", 4, RiscvRegType.GENERAL_PURPOSE)
        self.x4 = self.tp
        self.t0 = RiscvRegister("t0", 5, RiscvRegType.GENERAL_PURPOSE)
        self.x5 = self.t0
        self.t1 = RiscvRegister("t1", 6, RiscvRegType.GENERAL_PURPOSE)
        self.x6 = self.t1
        self.t2 = RiscvRegister("t2", 7, RiscvRegType.GENERAL_PURPOSE)
        self.x7 = self.t2
        self.s0 = RiscvRegister("s0", 8, RiscvRegType.GENERAL_PURPOSE)
        self.x8 = self.s0
        self.s1 = RiscvRegister("s1", 9, RiscvRegType.GENERAL_PURPOSE)
        self.x9 = self.s1
        self.a0 = RiscvRegister("a0", 10, RiscvRegType.GENERAL_PURPOSE)
        self.x10 = self.s0
        self.a1 = RiscvRegister("a1", 11, RiscvRegType.GENERAL_PURPOSE)
        self.x11 = self.a1
        self.a2 = RiscvRegister("a2", 12, RiscvRegType.GENERAL_PURPOSE)
        self.x12 = self.a2
        self.a3 = RiscvRegister("a3", 13, RiscvRegType.GENERAL_PURPOSE)
        self.x13 = self.a3
        self.a4 = RiscvRegister("a4", 14, RiscvRegType.GENERAL_PURPOSE)
        self.x14 = self.a4
        self.a5 = RiscvRegister("a5", 15, RiscvRegType.GENERAL_PURPOSE)
        self.x15 = self.a5
        if reg_count > 16:
            self.a6 = RiscvRegister("a6", 16, RiscvRegType.GENERAL_PURPOSE)
            self.x16 = self.a6
            self.a7 = RiscvRegister("a7", 17, RiscvRegType.GENERAL_PURPOSE)
            self.x17 = self.a7
            self.s2 = RiscvRegister("s2", 18, RiscvRegType.GENERAL_PURPOSE)
            self.x18 = self.s2
            self.s3 = RiscvRegister("s3", 19, RiscvRegType.GENERAL_PURPOSE)
            self.x19 = self.s3
            self.s4 = RiscvRegister("s4", 20, RiscvRegType.GENERAL_PURPOSE)
            self.x20 = self.s4
            self.s5 = RiscvRegister("s5", 21, RiscvRegType.GENERAL_PURPOSE)
            self.x21 = self.s5
            self.s6 = RiscvRegister("s6", 22, RiscvRegType.GENERAL_PURPOSE)
            self.x22 = self.s6
            self.s7 = RiscvRegister("s7", 23, RiscvRegType.GENERAL_PURPOSE)
            self.x23 = self.s7
            self.s8 = RiscvRegister("s8", 24, RiscvRegType.GENERAL_PURPOSE)
            self.x24 = self.s8
            self.s9 = RiscvRegister("s9", 25, RiscvRegType.GENERAL_PURPOSE)
            self.x25 = self.s9
            self.s10 = RiscvRegister("s10", 26, RiscvRegType.GENERAL_PURPOSE)
            self.x26 = self.s10
            self.s11 = RiscvRegister("s11", 27, RiscvRegType.GENERAL_PURPOSE)
            self.x27 = self.s11
            self.t3 = RiscvRegister("t3", 28, RiscvRegType.GENERAL_PURPOSE)
            self.x28 = self.t3
            self.t4 = RiscvRegister("t4", 29, RiscvRegType.GENERAL_PURPOSE)
            self.x29 = self.t4
            self.t5 = RiscvRegister("t5", 30, RiscvRegType.GENERAL_PURPOSE)
            self.x30 = self.t5
            self.t6 = RiscvRegister("t6", 31, RiscvRegType.GENERAL_PURPOSE)
            self.x31 = self.t6

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

