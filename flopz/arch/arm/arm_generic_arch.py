"""
higher-level arch for arm processors
"""

from flopz.arch.architecture import Architecture
from flopz.arch.register import Register
import enum


class ArmRegisterType(enum.IntEnum):
    GENERAL_PURPOSE = 1
    STACK_POINTER = 2
    LINK_REGISTER = 3
    PROGRAM_COUNTER = 4
    SPECIAL_PURPOSE = 5


class ArmRegister(Register):
    def __init__(self, name: str, val: int, reg_type: int = ArmRegisterType.GENERAL_PURPOSE):
        super(ArmRegister, self).__init__(name=f"r{name}", val=val, reg_type=reg_type)


class ARMGenericArchitecture(Architecture):
    def __init__(self, register_class=ArmRegister):
        super(ARMGenericArchitecture, self).__init__(register_class=register_class)
        # initialize general-purpose registers
        self.r0 = register_class(name="r0", val=0, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r1 = register_class(name="r1", val=1, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r2 = register_class(name="r2", val=2, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r3 = register_class(name="r3", val=3, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r4 = register_class(name="r4", val=4, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r5 = register_class(name="r5", val=5, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r6 = register_class(name="r6", val=6, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r7 = register_class(name="r7", val=7, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r8 = register_class(name="r8", val=8, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r9 = register_class(name="r9", val=9, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r10 = register_class(name="r10", val=10, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r11 = register_class(name="r11", val=11, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.r12 = register_class(name="r12", val=12, reg_type=ArmRegisterType.GENERAL_PURPOSE)
        self.sp = register_class(name="r13", val=13, reg_type=ArmRegisterType.STACK_POINTER)
        self.lr = register_class(name="r14", val=14, reg_type=ArmRegisterType.LINK_REGISTER)
        self.pc = register_class(name="r15", val=15, reg_type=ArmRegisterType.PROGRAM_COUNTER)
        self.xPSR = register_class(name="xPSR", val=16, reg_type=ArmRegisterType.SPECIAL_PURPOSE)

        self.registers = [getattr(self, f"r{i}") for i in range(0, 12)] + [self.sp, self.lr, self.pc, self.xPSR]

