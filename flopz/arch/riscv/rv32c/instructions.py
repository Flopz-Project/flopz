from bitstring import BitArray
from flopz.arch.riscv.rv32i.instructions import RiscvInstruction, RiscvInstructionForm
from flopz.arch.instruction import Instruction
from flopz.arch.exceptions import *
from flopz.arch.operands import BitsOperand
from flopz.util.integer_representation import representable, build_immediates
from flopz.arch.riscv.registers import RiscvRegister
from typing import Union


"""
C Extension for Compact Instructions is so far only implemented to Extend R32I
"""


"""
Utility Functions
"""


def get_compact_register_encoding(reg: Union[int, RiscvRegister]):
    """
    Returns the compact encoding for r8-r16.
    """
    if isinstance(reg, RiscvRegister):
        if reg.val in range(8, 16):
            return reg.val - 8
        else:
            raise ValueError(f"Register {reg.name} is not encodeable in compact format.")
    else:
        if reg in range(8, 16):
            return reg - 8
        else:
            raise ValueError(f"Register x{reg} is not encodeable in compact format.")


"""
Additional Instruction Forms
"""


class RiscvCompactInstructionForm(RiscvInstructionForm):
    """
    Compact instruction form base class.
    """
    def parse(self, instruction: Instruction):
        instruction.opcode_mask = BitArray(length=16, uint=0xC000)
        instruction.opcode = BitsOperand(instruction, 14, 16)


class RiscvCRForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct4 = BitsOperand(instruction, 0, 4)
        instruction.rd = BitsOperand(instruction, 4, 9)
        instruction.rs2 = BitsOperand(instruction, 9, 14)


class RiscvCIForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.imm1 = BitsOperand(instruction, 3, 4)
        instruction.rd = BitsOperand(instruction, 4, 9)
        instruction.imm2 = BitsOperand(instruction, 9, 14)


class RiscvCSSForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.imm = BitsOperand(instruction, 3, 9)
        instruction.rs2 = BitsOperand(instruction, 9, 14)


class RiscvCIWForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.imm = BitsOperand(instruction, 3, 11)
        instruction.rdc = BitsOperand(instruction, 11, 14)


class RiscvCLForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.imm1 = BitsOperand(instruction, 3, 6)
        instruction.rs1c = BitsOperand(instruction, 6, 9)
        instruction.imm2 = BitsOperand(instruction, 9, 11)
        instruction.rdc = BitsOperand(instruction, 11, 14)


class RiscvCSForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.imm1 = BitsOperand(instruction, 3, 6)
        instruction.rs1c = BitsOperand(instruction, 6, 9)
        instruction.imm2 = BitsOperand(instruction, 9, 11)
        instruction.rs2c = BitsOperand(instruction, 11, 14)


class RiscvCAForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct6 = BitsOperand(instruction, 0, 6)
        instruction.rdc = BitsOperand(instruction, 6, 9)
        instruction.funct2 = BitsOperand(instruction, 9, 11)
        instruction.rs2c = BitsOperand(instruction, 11, 14)


class RiscvCBForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.offset1 = BitsOperand(instruction, 3, 6)
        instruction.rs1c = BitsOperand(instruction, 6, 9)
        instruction.offset2 = BitsOperand(instruction, 9, 14)


class RiscvCJForm(RiscvCompactInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 0, 3)
        instruction.jt = BitsOperand(instruction, 3, 14)


"""
INSTRUCTIONS
"""

"""
LOADS AND STORES
"""


class CLWSP(RiscvInstruction):
    def __init__(self, rd, offset: int):
        if not representable(offset, 6, signed=False, shift=2):
            raise InvalidArgumentRangeException(f"Offset {offset} invalid.")
        if rd == 0:
            raise InvalidArgumentException(f"Register x0 is not addressable with this instruction.")
        imms = build_immediates(offset, ["[5]", "[4:2|7:6]"])
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b10, funct3=0b010, rd=rd, imm1=imms[0], imm2=imms[1])


class CSWSP(RiscvInstruction):
    def __init__(self, rs2, offset: int):
        if not representable(offset, 6, signed=False, shift=2):
            raise InvalidArgumentRangeException(f"Offset {offset} invalid.")
        super().__init__(RiscvCSSForm(), bit_length=16, opcode=0b10, funct3=0b110, rs2=rs2,
                         imm=build_immediates(offset, "[5:2|7:6]")[0])


class CLW(RiscvInstruction):
    def __init__(self, dest, base, offset: int):
        if not representable(offset, 5, signed=False, shift=2):
            raise InvalidArgumentRangeException(f"Offset {offset} invalid.")
        imms = build_immediates(offset, ["[5:3]", "[2|6]"])
        super().__init__(RiscvCLForm(), bit_length=16, opcode=0b00, funct3=0b010,
                         rs1c=get_compact_register_encoding(base), rdc=get_compact_register_encoding(dest),
                         imm1=imms[0], imm2=imms[1])


class CSW(RiscvInstruction):
    def __init__(self, src, base, offset: int):
        if not representable(offset, 5, signed=False, shift=2):
            raise InvalidArgumentRangeException(f"Offset {offset} invalid.")
        imms = build_immediates(offset, ["[5:3]", "[2|6]"])
        super().__init__(RiscvCSForm(), bit_length=16, opcode=0b00, funct3=0b110,
                         rs1c=get_compact_register_encoding(base), rs2c=get_compact_register_encoding(src),
                         imm1=imms[0], imm2=imms[1])


"""
CONTROL TRANSFER INSTRUCTIONS (JUMPS)
"""


class CJ(RiscvInstruction):
    def __init__(self, offset):
        if not representable(offset, 11, signed=True, shift=1):
            raise ValueError(f"Invalid offset {offset} for C.J instruction.")
        super().__init__(RiscvCJForm(), bit_length=16, opcode=0b01, funct3=0b101,
                         jt=build_immediates(offset, ["[11|4|9:8|10|6|7|3:1|5]"])[0])


class CJAL(RiscvInstruction):
    def __init__(self, offset):
        if not representable(offset, 11, signed=True, shift=1):
            raise ValueError(f"Invalid offset {offset} for C.JAL instruction.")
        super().__init__(RiscvCJForm(), bit_length=16, opcode=0b01, funct3=0b001,
                         jt=build_immediates(offset, ["[11|4|9:8|10|6|7|3:1|5]"])[0])


class CJR(RiscvInstruction):
    def __init__(self, rs1):
        if rs1.val == 0:
            raise ValueError("Register x0 invalid for C.JR instruction")
        super().__init__(RiscvCRForm(), bit_length=16, opcode=0b10, funct4=0b1000, rd=rs1, rs2=0)


class CJALR(RiscvInstruction):
    def __init__(self, rs1):
        if rs1.val == 0:
            raise ValueError("Register x0 invalid for C.JALR instruction")
        super().__init__(RiscvCRForm(), bit_length=16, opcode=0b10, funct4=0b1001, rd=rs1, rs2=0)


class CBEQZ(RiscvInstruction):
    def __init__(self, rs1, offset: int):
        if not representable(offset, 8, shift=1):
            raise ValueError(f"Offset {offset} not encodeable for this instruction.")
        imms = build_immediates(offset, ["[8|4:3]", "[7:6|2:1|5]"])
        super().__init__(RiscvCBForm(), bit_length=16, opcode=0b01, funct3=0b110,
                         rs1c=get_compact_register_encoding(rs1),
                         offset1=imms[0], offset2=imms[1])


class CBNEZ(RiscvInstruction):
    def __init__(self, rs1, offset: int):
        if not representable(offset, 8, shift=1):
            raise ValueError(f"Offset {offset} not encodeable for this instruction.")
        imms = build_immediates(offset, ["[8|4:3]", "[7:6|2:1|5]"])
        super().__init__(RiscvCBForm(), bit_length=16, opcode=0b01, funct3=0b111,
                         rs1c=get_compact_register_encoding(rs1),
                         offset1=imms[0], offset2=imms[1])


"""
INTEGER CONSTANT-GENERATION INSTRUCTIONS
"""


class CLI(RiscvInstruction):
    def __init__(self, rd, imm: int):
        if not representable(imm, 6):
            raise ValueError(f"Invalid immediate {imm}, has to be 6bit sign encodeable.")
        if rd.val == 0:
            raise ValueError("Register x0 invalid for C.LI instruction")
        imms = build_immediates(imm, ["[5]", "[4:0]"])
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b01, funct3=0b010, rd=rd,
                         imm1=imms[0], imm2=imms[1])


class CLUI(RiscvInstruction):
    def __init__(self, rd, imm: int):
        if not representable(imm, 6, shift=12):
            raise ValueError(f"Invalid immediate {imm}, not encodeable.")
        if imm == 0:
            raise ValueError(f"Invalid immediate {imm}, not valid for C.LUI instruction.")
        if rd.val == 0 or rd.val == 2:
            raise ValueError("Register x0 and x2 invalid for C.LUI instruction")
        imms = build_immediates(imm, ["[17]", "[16:12]"])
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b01, funct3=0b011, rd=rd,
                         imm1=imms[0], imm2=imms[1])


"""
INTEGER REGISTER-IMMEDIATE OPERATIONS
"""


class CADDI(RiscvInstruction):
    def __init__(self, rd, imm: int):
        if not representable(imm, 6):
            raise ValueError(f"Invalid immediate {imm}, has to be 6bit sign encodeable.")
        if imm == 0:
            raise ValueError("0 is an invalid immediate for C.ADDI instruction.")
        imms = build_immediates(imm, ["[5]", "[4:0]"])
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b01, funct3=0b000,
                         rd=rd, imm1=imms[0], imm2=imms[1])


class CADDI16SP(RiscvInstruction):
    def __init__(self, imm: int):
        if not representable(imm, 6, shift=4):
            raise ValueError(f"Invalid immediate {imm}, has to be 6bit sign encodeable when taken % 16.")
        if imm == 0:
            raise ValueError("0 is an invalid immediate for C.ADDI16SP instruction.")
        imms = build_immediates(imm, ["[9]", "[4|6|8:7|5]"])
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b01, funct3=0b011,
                         rd=2, imm1=imms[0], imm2=imms[1])


class CADDI4SPN(RiscvInstruction):
    def __init__(self, rd, imm: int):
        if not representable(imm, 8, signed=False, shift=2):
            raise ValueError(f"Invalid immediate {imm}, has to be 8bit encodeable when taken % 4.")
        if imm == 0:
            raise ValueError("0 is an invalid immediate for C.ADDI4SPN instruction.")
        imms = build_immediates(imm, ["[5:4|9:6|2|3]"])
        super().__init__(RiscvCIWForm(), bit_length=16, opcode=0b00, funct3=0b000,
                         rdc=get_compact_register_encoding(rd), imm=imms[0])


class CSLLI(RiscvInstruction):
    def __init__(self, rd, shift):
        if not representable(shift, 6, signed=False):
            raise ValueError(f"Invalid shift amount {shift} for C.SLLI instruction.")
        if rd.val == 0:
            raise ValueError(f"Register x0 is invalid for C.SLLI instruction.")
        imms = build_immediates(shift, ["[5]", "[4:0]"])
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b10, funct3=0b000,
                         rd=rd, imm1=imms[0], imm2=imms[1])


class CSRLI(RiscvInstruction):
    def __init__(self, rd, shift):
        if not representable(shift, 6, signed=False):
            raise ValueError(f"Invalid shift amount {shift} for C.SRLI instruction.")
        imms = build_immediates(shift, ["[5]", "[4:0]"])
        super().__init__(RiscvCBForm(), bit_length=16, opcode=0b01, funct3=0b100,
                         rs1c=get_compact_register_encoding(rd), offset1=imms[0] << 2, offset2=imms[1])


class CSRAI(RiscvInstruction):
    def __init__(self, rd, shift):
        if not representable(shift, 6, signed=False):
            raise ValueError(f"Invalid shift amount {shift} for C.SRAI instruction.")
        imms = build_immediates(shift, ["[5]", "[4:0]"])
        super().__init__(RiscvCBForm(), bit_length=16, opcode=0b01, funct3=0b100,
                         rs1c=get_compact_register_encoding(rd), offset1=(imms[0] << 2) + 1, offset2=imms[1])


class CANDI(RiscvInstruction):
    def __init__(self, rd, imm):
        if not representable(imm, 6):
            raise ValueError(f"Invalid shift amount {imm} for C.ANDI instruction.")
        imms = build_immediates(imm, ["[5]", "[4:0]"])
        super().__init__(RiscvCBForm(), bit_length=16, opcode=0b01, funct3=0b100,
                         rs1c=get_compact_register_encoding(rd), offset1=(imms[0] << 2) + 2, offset2=imms[1])


"""
INTEGER REGISTER-REGISTER OPERATIONS
"""


class CMV(RiscvInstruction):
    def __init__(self, rd, rs2):
        if rd.val == 0 or rs2.val == 0:
            raise ValueError(f"Register x0 not valid for C.MV instruction.")
        super().__init__(RiscvCRForm(), bit_length=16, opcode=0b10, funct4=0b1000,
                         rd=rd, rs2=rs2)


class CADD(RiscvInstruction):
    def __init__(self, rd, rs2):
        if rd.val == 0 or rs2.val == 0:
            raise ValueError(f"Register x0 not valid for C.ADD instruction.")
        super().__init__(RiscvCRForm(), bit_length=16, opcode=0b10, funct4=0b1001,
                         rd=rd, rs2=rs2)


class CAND(RiscvInstruction):
    def __init__(self, rd, rs2):
        super().__init__(RiscvCAForm(), bit_length=16, opcode=0b01, funct6=0b100011, funct2=0b11,
                         rdc=get_compact_register_encoding(rd), rs2c=get_compact_register_encoding(rs2))


class COR(RiscvInstruction):
    def __init__(self, rd, rs2):
        super().__init__(RiscvCAForm(), bit_length=16, opcode=0b01, funct6=0b100011, funct2=0b10,
                         rdc=get_compact_register_encoding(rd), rs2c=get_compact_register_encoding(rs2))


class CXOR(RiscvInstruction):
    def __init__(self, rd, rs2):
        super().__init__(RiscvCAForm(), bit_length=16, opcode=0b01, funct6=0b100011, funct2=0b01,
                         rdc=get_compact_register_encoding(rd), rs2c=get_compact_register_encoding(rs2))


class CSUB(RiscvInstruction):
    def __init__(self, rd, rs2):
        super().__init__(RiscvCAForm(), bit_length=16, opcode=0b01, funct6=0b100011, funct2=0b00,
                         rdc=get_compact_register_encoding(rd), rs2c=get_compact_register_encoding(rs2))


"""
NOP AND BREAK
"""


class CNOP(RiscvInstruction):
    def __init__(self):
        super().__init__(RiscvCIForm(), bit_length=16, opcode=0b01, funct3=0b000,
                         rd=0, imm1=0, imm2=0)


class CEBREAK(RiscvInstruction):
    def __init__(self):
        super().__init__(RiscvCRForm(), bit_length=16, opcode=0b10, funct4=0b1001,
                         rd=0, rs2=0)


# TODO replace reg.val with something that can handle integers too

