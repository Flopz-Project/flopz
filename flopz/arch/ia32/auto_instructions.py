from flopz.arch.auto_instruction import AutoInstruction
from flopz.arch.ia32.instructions import *
from flopz.arch.ia32.conditionals import Cond
from typing import List, Union


class IA32AutoInstruction(AutoInstruction):
    def __init__(self):
        super().__init__()
        self.instruction = None

    def expand(self) -> List[IA32Instruction]:
        return [self.instruction]


"""
MOV
"""


class Mov(IA32AutoInstruction):
    def __init__(self, dst, src):
        super().__init__()
        if isinstance(dst, IA32Register) and isinstance(src, IA32Register):
            self.instruction = MovRegToReg(dst, src)
        elif isinstance(dst, MemoryAddress) and isinstance(src, IA32Register):
            self.instruction = MovRegToMem(dst, src)
        elif isinstance(dst, IA32Register) and isinstance(src, MemoryAddress):
            self.instruction = MovMemToReg(dst, src)
        elif isinstance(dst, IA32Register) and isinstance(src, int):
            self.instruction = MovImmToReg(dst, src)
        elif isinstance(dst, MemoryAddress) and isinstance(src, int):
            self.instruction = MovImmToMem(dst, src)
        else:
            raise TypeError(f"Arguments of type {type(dst)} and {type(src)} are not valid for MOV.")


"""
ADD
"""


class Add(IA32AutoInstruction):
    def __init__(self, dst: Union[IA32Register, MemoryAddress], src: Union[IA32Register, MemoryAddress, int]):
        super().__init__()
        if isinstance(dst, IA32Register) and isinstance(src, int):
            self.instruction = AddImmToReg(dst, src)
        elif isinstance(dst, MemoryAddress) and isinstance(src, int):
            self.instruction = AddImmToMem(dst, src)
        elif isinstance(dst, IA32Register) and isinstance(src, IA32Register):
            self.instruction = AddRegToReg(dst, src)
        elif isinstance(dst, MemoryAddress) and isinstance(src, IA32Register):
            self.instruction = AddRegToMem(dst, src)
        elif isinstance(dst, IA32Register) and isinstance(src, MemoryAddress):
            self.instruction = AddMemToReg(dst, src)
        else:
            raise TypeError(f"Arguments of type {type(dst)} and {type(src)} are not valid for ADD.")


"""
JMP
"""


class Jmp(IA32AutoInstruction):
    def __init__(self, addr: Union[IA32Register, MemoryAddress]):
        super().__init__()
        if isinstance(addr, IA32Register):
            self.instruction = JmpToReg(addr)
        elif isinstance(addr, MemoryAddress):
            self.instruction = JmpToMem(addr)
        else:
            raise TypeError(f"Invalid argument of type {type(addr)} for JMP")


class Jcc(IA32AutoInstruction):
    def __init__(self, cond: Cond, rel: int):
        super().__init__()
        self.instruction = JmpCond(cond, rel)


"""
SHIFTS
"""


class SAL(IA32AutoInstruction):
    def __init__(self, target: Union[IA32Register, MemoryAddress], shift: int):
        super().__init__()
        self.instruction = Shift(target, shift, 4)


class SHL(IA32AutoInstruction):
    def __init__(self, target: Union[IA32Register, MemoryAddress], shift: int):
        super().__init__()
        self.instruction = Shift(target, shift, 4)


class SAR(IA32AutoInstruction):
    def __init__(self, target: Union[IA32Register, MemoryAddress], shift: int):
        super().__init__()
        self.instruction = Shift(target, shift, 7)


class SHR(IA32AutoInstruction):
    def __init__(self, target: Union[IA32Register, MemoryAddress], shift: int):
        super().__init__()
        self.instruction = Shift(target, shift, 5)


"""
Logicals
"""


class AND(IA32AutoInstruction):
    def __init__(self, dst: Union[IA32Register, MemoryAddress], src: Union[IA32Register, MemoryAddress, int]):
        super().__init__()
        if isinstance(src, int):
            self.instruction = LogicImm(dst, src, reg_code=4)
        elif isinstance(src, IA32Register):
            self.instruction = LogicRegToMem(dst, src, reg_code=4)
        elif isinstance(src, MemoryAddress):
            self.instruction = LogicMemToReg(dst, src, reg_code=4)
        else:
            raise TypeError(f"Invalid argument types ({type(dst)}, {type(src)}) for logical instruction.")


class OR(IA32AutoInstruction):
    def __init__(self, dst: Union[IA32Register, MemoryAddress], src: Union[IA32Register, MemoryAddress, int]):
        super().__init__()
        if isinstance(src, int):
            self.instruction = LogicImm(dst, src, reg_code=1)
        elif isinstance(src, IA32Register):
            self.instruction = LogicRegToMem(dst, src, reg_code=1)
        elif isinstance(src, MemoryAddress):
            self.instruction = LogicMemToReg(dst, src, reg_code=1)
        else:
            raise TypeError(f"Invalid argument types ({type(dst)}, {type(src)}) for logical instruction.")


class XOR(IA32AutoInstruction):
    def __init__(self, dst: Union[IA32Register, MemoryAddress], src: Union[IA32Register, MemoryAddress, int]):
        super().__init__()
        if isinstance(src, int):
            self.instruction = LogicImm(dst, src, reg_code=6)
        elif isinstance(src, IA32Register):
            self.instruction = LogicRegToMem(dst, src, reg_code=6)
        elif isinstance(src, MemoryAddress):
            self.instruction = LogicMemToReg(dst, src, reg_code=6)
        else:
            raise TypeError(f"Invalid argument types ({type(dst)}, {type(src)}) for logical instruction.")

