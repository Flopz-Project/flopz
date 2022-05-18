from flopz.arch.instruction import Instruction
from flopz.arch.ia32.addressing import IA32Register, MemoryAddress, IA32RegType
from flopz.arch.ia32.instruction_components import IA32Opcode, Immediate, ModRM, Displacement, SIB
from flopz.util.integer_representation import representable
from flopz.arch.ia32.conditionals import Cond

from typing import Union


"""
Instructions
"""


class IA32Instruction(Instruction):
    """
    Base class for all IA32 instructions.

    The class holds all the instruction components (opcode, ModRM, SIB, displacement, immediate) and builds
    the full encoding from the components.
    """
    def __init__(self, opcode: IA32Opcode, modrm=None, sib=None, displacement=None,
                 immediate=None, addr=0):

        self.opcode = opcode
        self.modrm = modrm
        self.sib = sib
        self.displacement = displacement
        self.immediate = immediate

        # encode parts of the instruction
        encoding = self.opcode.encode()
        if self.modrm is not None:
            encoding.append(self.modrm.encode())
        if self.sib is not None:
            encoding.append(self.sib.encode())
        if self.displacement is not None:
            encoding.append(self.displacement.encode())
        if self.immediate is not None:
            encoding.append(self.immediate.encode())

        bit_length = encoding.len

        super().__init__('', addr, bit_length)
        self.bits = encoding.copy()

    def bytes(self) -> bytes:
        return self.bits.bytes

    def check_arg_compatibility(self, dst, src):
        if not dst.bit_size == src.bit_size:
            raise Exception("Incompatible arguments.")


"""
MOV
"""


class MovRegToReg(IA32Instruction):
    def __init__(self, dst: IA32Register, src: IA32Register):

        if dst.type == IA32RegType.GENERAL_PURPOSE and src.type == IA32RegType.GENERAL_PURPOSE:
            self.check_arg_compatibility(dst, src)
            if dst.bit_size == 8:
                opcode = IA32Opcode(0x88, op_size=dst.bit_size, force_rex=dst.requires_rex() or src.requires_rex())
            else:
                opcode = IA32Opcode(0x89, op_size=dst.bit_size)
            modrm = ModRM(reg=src.val, rm=dst.val, opcode=opcode)
        elif dst.type == IA32RegType.SEGMENT and src.type == IA32RegType.GENERAL_PURPOSE:
            if src.bit_size not in (16, 64):
                raise ValueError("Invalid Register for Mov to Segment Register")
            opcode = IA32Opcode(0x8E, op_size=src.bit_size)
            modrm = ModRM(reg=dst.val, rm=src.val)
        elif dst.type == IA32RegType.GENERAL_PURPOSE and src.type == IA32RegType.SEGMENT:
            if dst.bit_size not in (16, 64):
                raise ValueError("Invalid Register for Mov from Segment Register")
            opcode = IA32Opcode(0x8C, op_size=dst.bit_size)
            modrm = ModRM(reg=src.val, rm=dst.val)
        else:
            raise ValueError("invalid Register Type Combination for Mov")

        super().__init__(opcode=opcode, modrm=modrm)

    def check_arg_compatibility(self, dst, src):
        if not dst.bit_size == src.bit_size:
            raise Exception("Incompatible arguments.")
        if dst.requires_rex() or src.requires_rex():
            if dst.is_high() or src.is_high():
                raise Exception("Invalid to encode this register combination")


class MovRegToMem(IA32Instruction):
    def __init__(self, dst: MemoryAddress, src: IA32Register):
        if src.type == IA32RegType.GENERAL_PURPOSE:
            self.check_arg_compatibility(dst, src)
            if dst.bit_size == 8:
                opcode = IA32Opcode(0x88, op_size=8, force_rex=src.requires_rex())
            else:
                opcode = IA32Opcode(0x89, op_size=dst.bit_size)
            modrm, sib, disp = dst.get_encoding(opcode=opcode)
            modrm.reg = src.val
        elif src.type == IA32RegType.SEGMENT:
            if dst.bit_size not in (16, 64):
                raise ValueError("Invalid MemoryAddress size for Mov from Segment Register")
            opcode = IA32Opcode(0x8C, op_size=src.bit_size)
            modrm, sib, disp = dst.get_encoding()
            modrm.reg = src.val
        else:
            raise ValueError("Invalid Register Type for Mov to Memory")

        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)


class MovMemToReg(IA32Instruction):
    def __init__(self, dst: IA32Register, src: MemoryAddress):
        if dst.type == IA32RegType.GENERAL_PURPOSE:
            self.check_arg_compatibility(dst, src)
            if dst.bit_size == 8:
                opcode = IA32Opcode(0x8A, op_size=8, force_rex=dst.requires_rex())
            else:
                opcode = IA32Opcode(0x8B, op_size=dst.bit_size)
            modrm, sib, disp = src.get_encoding(opcode=opcode)
            modrm.reg = dst.val
        elif dst.type == IA32RegType.SEGMENT:
            if src.bit_size not in (16, 64):
                raise ValueError("Invalid MemoryAddress size for Mov to Segment Register")
            opcode = IA32Opcode(0x8E, op_size=src.bit_size)
            modrm, sib, disp = src.get_encoding()
            modrm.reg = dst.val
        else:
            raise ValueError("Invalid Register Type for Mov from Memory")

        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)


class MovImmToReg(IA32Instruction):
    def __init__(self, dst: IA32Register, src: int):
        self.check_arg_compatibility(dst, src)

        if dst.bit_size == 8:
            opcode = IA32Opcode(0xB0, op_size=8, force_rex=dst.requires_rex(), opc_encoding=dst.val)
        else:
            opcode = IA32Opcode(0xB8, op_size=dst.bit_size, opc_encoding=dst.val)
        imm = Immediate(src, dst.bit_size//8)

        super().__init__(opcode=opcode, immediate=imm)

    def check_arg_compatibility(self, dst, src):
        if not representable(src, min(dst.bit_size, 32), signed=True):
            raise Exception("Immediate not fit for register")


class MovImmToMem(IA32Instruction):
    def __init__(self, dst: MemoryAddress, src: int):
        self.check_arg_compatibility(dst, src)

        if dst.bit_size == 8:
            opcode = IA32Opcode(0xC6, op_size=8)
        else:
            opcode = IA32Opcode(0xC7, op_size=dst.bit_size)
        modrm, sib, disp = dst.get_encoding(opcode=opcode)
        modrm.reg = 0  # unused reg field has to be 0
        imm = Immediate(src, min(dst.bit_size//8, 4))

        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp, immediate=imm)

    def check_arg_compatibility(self, dst, src):
        if not representable(src, dst.bit_size, signed=True):
            raise Exception("Immediate not fit for register")


"""
ADD
"""


class AddImmToReg(IA32Instruction):
    def __init__(self, dst: IA32Register, src: int):
        if not representable(src, 32):
            raise ValueError(f"Invalid addend {src} for Add")

        if dst.bit_size == 8:
            opcode = IA32Opcode(0x80, op_size=8, force_rex=dst.requires_rex())
        else:
            opcode = IA32Opcode(0x81, op_size=dst.bit_size)
        modrm = ModRM(rm=dst.val, opcode=opcode)
        imm = Immediate(src, min(dst.bit_size//8, 4))
        super().__init__(opcode=opcode, modrm=modrm, immediate=imm)


class AddImmToMem(IA32Instruction):
    def __init__(self, dst: MemoryAddress, src: int):
        if not representable(src, 32):
            raise ValueError(f"Invalid addend {src} for Add")
        if dst.bit_size == 8:
            opcode = IA32Opcode(0x80, op_size=8)
        else:
            opcode = IA32Opcode(0x81, op_size=dst.bit_size)
        modrm, sib, disp = dst.get_encoding(opcode=opcode)
        imm = Immediate(src, min(dst.bit_size // 8, 4))
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp, immediate=imm)


class AddRegToReg(IA32Instruction):
    def __init__(self, dst: IA32Register, src: IA32Register):
        self.check_arg_compatibility(dst, src)

        if dst.bit_size == 8:
            opcode = IA32Opcode(0x00, op_size=8, force_rex=src.requires_rex() or dst.requires_rex())
        else:
            opcode = IA32Opcode(0x01, op_size=dst.bit_size)
        modrm = ModRM(reg=src.val, rm=dst.val, opcode=opcode)
        super().__init__(opcode=opcode, modrm=modrm)

    def check_arg_compatibility(self, dst, src):
        if not dst.bit_size == src.bit_size:
            raise Exception("Incompatible arguments.")
        if dst.requires_rex() or src.requires_rex():
            if dst.is_high() or src.is_high():
                raise Exception("Invalid to encode this register combination")


class AddRegToMem(IA32Instruction):
    def __init__(self, dst: MemoryAddress, src: IA32Register):
        self.check_arg_compatibility(dst, src)

        if dst.bit_size == 8:
            opcode = IA32Opcode(0x00, op_size=8, force_rex=src.requires_rex())
        else:
            opcode = IA32Opcode(0x01, op_size=dst.bit_size)
        modrm, sib, disp = dst.get_encoding(opcode=opcode)
        modrm.reg = src.val
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)


class AddMemToReg(IA32Instruction):
    def __init__(self, dst: IA32Register, src: MemoryAddress):
        self.check_arg_compatibility(dst, src)

        if src.bit_size == 8:
            opcode = IA32Opcode(0x02, op_size=8, force_rex=dst.requires_rex())
        else:
            opcode = IA32Opcode(0x03, op_size=src.bit_size)
        modrm, sib, disp = src.get_encoding(opcode=opcode)
        modrm.reg = dst.val
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)


"""
JUMPS
"""


class JmpToReg(IA32Instruction):
    def __init__(self, addr: IA32Register):
        opcode = IA32Opcode(0xFF, op_size=32)
        modrm = ModRM(reg=4, rm=addr.val, opcode=opcode)
        super().__init__(opcode=opcode, modrm=modrm)


class JmpToMem(IA32Instruction):
    def __init__(self, addr: MemoryAddress):
        opcode = IA32Opcode(0xFF, op_size=32)
        modrm, sib, disp = addr.get_encoding(opcode=opcode)
        modrm.reg = 4
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)


class JmpCond(IA32Instruction):
    def __init__(self, cond: Cond, rel: int):
        if representable(rel, 8):
            opcode = IA32Opcode(0x70 + cond, op_size=32)
            imm = Immediate(rel, 1)
        elif representable(rel, 64):
            if cond == Cond.RCXZ:
                raise ValueError("Cond RCXZ not valid for near Jccs (only short 8bit).")
            opcode = IA32Opcode(0x0F80 + cond, op_size=32)
            imm = Immediate(rel, 4)
        else:
            raise ValueError(f"Relative offset {rel} too big for near jump.")
        super().__init__(opcode=opcode, immediate=imm)


"""
SHIFTS
"""


class Shift(IA32Instruction):
    def __init__(self, target: Union[IA32Register, MemoryAddress], shift: Union[int, IA32Register], shift_type: int):
        op_size = target.bit_size

        # valid type ints are 4 (SAL, SHL), 5 (SHR) and 7 (SAR)
        if shift_type not in (4, 5, 7):
            raise ValueError(f"Invalid shift parameter {shift_type}, valid are 4, 5 or 7.")

        if isinstance(shift, int):
            # count is masked to 5 (or 6 if REX.w) bits, so check for valid shifts
            if op_size == 64 and shift not in range(64) or op_size < 64 and shift not in range(32):
                raise ValueError(f"Invalid shift operand {shift}, valid values are 0..31 (or 0..63 for 64bit operand"
                                 f" instructions.")
            oc_val = 0xD0 if shift == 1 else 0xC0
        elif isinstance(shift, IA32Register):
            if not shift.name == "cl":
                raise ValueError("Only cl register can be used for shifts.")
            oc_val = 0xD2
        else:
            raise TypeError("Shift parameter has to be either int or cl register.")

        if op_size == 8:
            force = True if isinstance(target, IA32Register) and target.requires_rex() else False
            opcode = IA32Opcode(oc_val, op_size=8, force_rex=force)
        else:
            opcode = IA32Opcode(oc_val + 1, op_size=op_size)
        if isinstance(target, IA32Register):
            modrm = ModRM(reg=shift_type, rm=target.val, opcode=opcode)
            sib, disp = (None, None)
        elif isinstance(target, MemoryAddress):
            modrm, sib, disp = target.get_encoding(opcode=opcode)
            modrm.reg = shift_type
        else:
            raise TypeError(f"Invalid target type {type(target)} for Shift instruction.")
        if isinstance(shift, int) and shift > 1:
            imm = Immediate(shift, 1)
        else:
            imm = None
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp, immediate=imm)


"""
LOGICALS
"""


class LogicImm(IA32Instruction):
    def __init__(self, dst: Union[IA32Register, MemoryAddress], imm: int, reg_code: int):
        op_size = dst.bit_size

        if not representable(imm, min(op_size, 32)):
            raise ValueError(f"Immediate {imm} not valid for {op_size}bit logic instruction.")

        # OR 1, AND 4, XOR 6
        if reg_code not in (1, 4, 6):
            raise ValueError("Invalid reg_code to encode with immediate logical instruction.")

        if op_size == 8:
            force = True if isinstance(dst, IA32Register) and dst.requires_rex() else False
            opcode = IA32Opcode(0x80, op_size=8, force_rex=force)
        else:
            opcode = IA32Opcode(0x81, op_size=op_size)
        if isinstance(dst, IA32Register):
            modrm = ModRM(reg=reg_code, rm=dst.val, opcode=opcode)
            sib, disp = (None, None)
        elif isinstance(dst, MemoryAddress):
            modrm, sib, disp = dst.get_encoding(opcode=opcode)
            modrm.reg = reg_code
        else:
            raise TypeError("Invalid dst for Logical Instruction!")
        imm = Immediate(imm, min(op_size, 32) // 8)
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, immediate=imm, displacement=disp)


class LogicRegToMem(IA32Instruction):  # dst can be mem or reg
    def __init__(self, dst: Union[IA32Register, MemoryAddress], src: IA32Register, reg_code: int):
        op_size = dst.bit_size

        # OR 1, AND 4, XOR 6
        if reg_code == 1:
            oc_val = 0x08
        elif reg_code == 4:
            oc_val = 0x20
        elif reg_code == 6:
            oc_val = 0x30
        else:
            raise ValueError("Invalid reg_code to encode with immediate logical instruction.")

        if op_size == 8:
            force = True if isinstance(dst, IA32Register) and dst.requires_rex() else False
            opcode = IA32Opcode(oc_val, op_size=8, force_rex=force)
        else:
            opcode = IA32Opcode(oc_val+1, op_size=op_size)
        if isinstance(dst, IA32Register):
            modrm = ModRM(reg=src.val, rm=dst.val, opcode=opcode)
            sib, disp = (None, None)
        elif isinstance(dst, MemoryAddress):
            modrm, sib, disp = dst.get_encoding(opcode=opcode)
            modrm.reg = src.val
        else:
            raise TypeError("Invalid dst for Logical Instruction!")
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)


class LogicMemToReg(IA32Instruction):  # src can be mem or reg
    def __init__(self, dst: IA32Register, src: Union[IA32Register, MemoryAddress], reg_code: int):
        op_size = dst.bit_size

        # OR 1, AND 4, XOR 6
        if reg_code == 1:
            oc_val = 0x0A
        elif reg_code == 4:
            oc_val = 0x22
        elif reg_code == 6:
            oc_val = 0x32
        else:
            raise ValueError("Invalid reg_code to encode with immediate logical instruction.")

        if op_size == 8:
            opcode = IA32Opcode(oc_val, op_size=8, force_rex=dst.requires_rex())
        else:
            opcode = IA32Opcode(oc_val + 1, op_size=op_size)
        if isinstance(src, IA32Register):
            modrm = ModRM(reg=dst.val, rm=src.val, opcode=opcode)
            sib, disp = (None, None)
        elif isinstance(src, MemoryAddress):
            modrm, sib, disp = src.get_encoding(opcode=opcode)
            modrm.reg = dst.val
        else:
            raise TypeError("Invalid dst for Logical Instruction!")
        super().__init__(opcode=opcode, modrm=modrm, sib=sib, displacement=disp)

