from typing import List
from flopz.arch.register import Register
from flopz.arch.auto_instruction import AutoInstruction
from flopz.arch.ppc.vle.instructions import *


class AutoLoadI(AutoInstruction):
    def __init__(self, rD: Register, imm: int):
        super(AutoLoadI, self).__init__() # leave register at 0
        self.rD = rD
        self.imm = imm

    def expand(self) -> List[Instruction]:
        # the immediate decides how we'll handle this
        if self.imm in range(0, 0x80):
            return [SeLi(self.rD, self.imm)]
        elif self.imm in range(-0x7ffff, 0x80000):
            # i20
            return [ELi(self.rD, self.imm)]
        else:
            # use two instructions: load shifted and add
            immediate_upper = self.imm & 0xFFFF0000
            diff = self.imm - immediate_upper
            if abs(diff) < 0x8000:
                # we can use load & add
                load_shifted = ELis(self.rD, immediate_upper >> 16)
                add_or_sub = EAdd16i(self.rD, self.rD, diff)
                # we can use a 2 bytes addi if the offset is small enough
                if diff in range(1,32):
                    add_or_sub = SeAddi(self.rD, diff)
                return [load_shifted, add_or_sub]
            else:
                raise Exception("AuoLoadI: Not implemented!")


