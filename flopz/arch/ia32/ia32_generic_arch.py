"""
higher-level arch for IA-32 processors
"""

from flopz.arch.architecture import Architecture
from flopz.arch.ia32.registers import IA32_Register

import enum


class ProcessorMode(enum.IntEnum):
    LONG = 0
    PROTECTED = 1


class IA32RegType(enum.IntEnum):
    GENERAL_PURPOSE = 0
    SEGMENT = 1
    EFLAGS = 2
    EIP = 3
    FPU = 4
    MMX = 5
    XMM = 6


class IA32GenericArchitecture(Architecture):
    def __init__(self, register_class=IA32_Register, mode=ProcessorMode.LONG):
        super().__init__(register_class=register_class)

        self.mode = mode

        __reg_name_map = ['a', 'c', 'd', 'b', 'sp', 'bp', 'si', 'di']

        for i in range(16):
            # add 8 bit register
            if i < 8:
                self.set_register(IA32_Register(__reg_name_map[i]+"l", i,
                                                                   IA32RegType.GENERAL_PURPOSE, bit_size=8))
                if i < 4:
                    self.set_register(IA32_Register(__reg_name_map[i]+"h", i,
                                                                       IA32RegType.GENERAL_PURPOSE,bit_size=8,
                                                                       is_high=True))
            else:
                self.set_register(IA32_Register(f"r{i}b", i, IA32RegType.GENERAL_PURPOSE, bit_size=8))

            # add 16bit register
            if i < 4:
                self.set_register(IA32_Register(f"{__reg_name_map[i]}x", i,
                                                                     IA32RegType.GENERAL_PURPOSE, bit_size=16))
            elif i < 8:
                self.set_register(IA32_Register(f"{__reg_name_map[i]}", i,
                                                                     IA32RegType.GENERAL_PURPOSE, bit_size=16))
            else:
                self.set_register(IA32_Register(f"r{i}w", i, IA32RegType.GENERAL_PURPOSE, bit_size=16))

            # add 32bit Register
            if i < 4:
                self.set_register(IA32_Register(f"e{__reg_name_map[i]}x", i,
                                                                     IA32RegType.GENERAL_PURPOSE, bit_size=32))
            elif i < 8:
                self.set_register(IA32_Register(f"e{__reg_name_map[i]}", i,
                                                                     IA32RegType.GENERAL_PURPOSE, bit_size=32))
            else:
                self.set_register(IA32_Register(f"r{i}d", i, IA32RegType.GENERAL_PURPOSE, bit_size=32))

            # add 64bit register
            if i < 4:
                self.set_register(IA32_Register(f"r{__reg_name_map[i]}x", i,
                                                                     IA32RegType.GENERAL_PURPOSE, bit_size=64))
            elif i < 8:
                self.set_register(IA32_Register(f"r{__reg_name_map[i]}", i,
                                                                     IA32RegType.GENERAL_PURPOSE, bit_size=64))
            else:
                self.set_register(IA32_Register(f"r{i}", i, IA32RegType.GENERAL_PURPOSE, bit_size=64))

    def set_register(self, reg):
        setattr(self, reg.name, reg)
        self.registers.append(reg)
