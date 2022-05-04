from bitstring import BitArray
from flopz.arch.instruction import Instruction
from flopz.arch.exceptions import *
from flopz.arch.operands import BitsOperand, CombinedOperand


class RiscvInstructionForm:
    """
    Base class for the different forms a riscv instruction can have.
    Forms add the operands to the instruction object with their parse function.
    """
    def parse(self, instruction: Instruction):
        instruction.opcode_mask = BitArray(length=32, uint=0xFE000000)
        instruction.opcode = BitsOperand(instruction, 25, 32)


class RiscvRForm(RiscvInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.rd = BitsOperand(instruction, 20, 25)
        instruction.funct3 = BitsOperand(instruction, 17, 20)
        instruction.rs1 = BitsOperand(instruction, 12, 17)
        instruction.rs2 = BitsOperand(instruction, 7, 12)
        instruction.funct7 = BitsOperand(instruction, 0, 7)


class RiscvIForm(RiscvInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.rd = BitsOperand(instruction, 20, 25)
        instruction.funct3 = BitsOperand(instruction, 17, 20)
        instruction.rs1 = BitsOperand(instruction, 12, 17)
        instruction.imm = BitsOperand(instruction, 0, 12, signed=True)


class RiscvSForm(RiscvInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 17, 20)
        instruction.rs1 = BitsOperand(instruction, 12, 17)
        instruction.rs2 = BitsOperand(instruction, 7, 12)
        instruction.imm = CombinedOperand(BitsOperand(instruction, 0, 7), BitsOperand(instruction, 20, 25), signed=True)


class RiscvBForm(RiscvInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.funct3 = BitsOperand(instruction, 17, 20)
        instruction.rs1 = BitsOperand(instruction, 12, 17)
        instruction.rs2 = BitsOperand(instruction, 7, 12)
        instruction.imm = CombinedOperand(BitsOperand(instruction, 0, 1),
                                          BitsOperand(instruction, 24, 25),
                                          BitsOperand(instruction, 1, 7),
                                          BitsOperand(instruction, 20, 24),
                                          signed=True, shift=1)


class RiscvUForm(RiscvInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.rd = BitsOperand(instruction, 20, 25)
        instruction.imm = BitsOperand(instruction, 0, 20, signed=True, shift=12)


class RiscvJForm(RiscvInstructionForm):
    def parse(self, instruction: Instruction):
        super().parse(instruction)
        instruction.rd = BitsOperand(instruction, 20, 25)
        instruction.imm = CombinedOperand(BitsOperand(instruction, 0, 1),
                                          BitsOperand(instruction, 12, 20),
                                          BitsOperand(instruction, 11, 12),
                                          BitsOperand(instruction, 1, 11),
                                          signed=True, shift=1)


"""
INSTRUCTIONS
"""


class RiscvInstruction(Instruction):
    """
    Base class for all RiscV instructions.

    Will parse the given InstructionForm instance to add the operands to the instruction and
    then use the keyword arguments to set the different operands.
    """
    def __init__(self, form: RiscvInstructionForm, addr: int = 0, bit_length: int = 32, **kwargs):
        super().__init__('', addr, bit_length)

        self.instruction_form = form
        self.instruction_form.parse(self)

        # apply the operands using kwargs
        for k, v in kwargs.items():
            operand = getattr(self, k)
            operand(v)

    def bytes(self) -> bytes:
        swapped_bytes = self.bits.copy()
        swapped_bytes.byteswap()
        return swapped_bytes.bytes


"""
INTEGER REGISTER-IMMEDIATE INSTRUCTIONS
"""


# Add Immediate
class R32iADDI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b000, rd=rd, rs1=rs, imm=imm)


# Set Less Then Immediate
class R32iSLTI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b010, rd=rd, rs1=rs, imm=imm)


# Set Less Then Immediate (Unsigned)
class R32iSLTIU(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b011, rd=rd, rs1=rs, imm=imm)


# XOR Immediate
class R32iXORI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b100, rd=rd, rs1=rs, imm=imm)


# OR Immediate
class R32iORI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b110, rd=rd, rs1=rs, imm=imm)


# AND Immediate
class R32iANDI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b111, rd=rd, rs1=rs, imm=imm)


# Shift left logical by Immediate
class R32iSLLI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        if imm not in range(32):
            raise InvalidArgumentRangeException("Shift not in valid range")
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b001, rd=rd, rs1=rs, imm=imm)


# Shift right logical by Immediate
class R32iSRLI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        if imm not in range(32):
            raise InvalidArgumentRangeException("Shift not in valid range")
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b101, rd=rd, rs1=rs, imm=imm)


# Shift right arithmetic by Immediate
class R32iSRAI(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        if imm not in range(32):
            raise InvalidArgumentRangeException("Shift not in valid range")
        super().__init__(RiscvIForm(), opcode=0b10011, funct3=0b101, rd=rd, rs1=rs, imm=imm+1024)


# Load upper Immediate
class R32iLUI(RiscvInstruction):
    def __init__(self, rd, imm):
        super().__init__(RiscvUForm(), opcode=0b0110111, rd=rd, imm=imm)


# Add upper Immediate to PC
class R32iAUIPC(RiscvInstruction):
    def __init__(self, rd, imm):
        super().__init__(RiscvUForm(), opcode=0b0010111, rd=rd, imm=imm)


"""
INTEGER REGISTER-REGISTER INSTRUCTIONS
"""


# Add
class R32iADD(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b000, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


# Sub
class R32iSUB(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b000, funct7=32, rd=rd, rs1=rs1, rs2=rs2)


# Shift Logical Left
class R32iSLL(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b001, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


# Set Less Then
class SLT(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b010, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


# Set Less Then (Unsigned)
class R32iSLTU(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b011, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


class R32iXOR(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b100, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


# Shift Right Logical
class R32iSRL(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b101, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


# Shift Right Arithmetic
class R32iSRA(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b101, funct7=32, rd=rd, rs1=rs1, rs2=rs2)


class R32iOR(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b110, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


class R32iAND(RiscvInstruction):
    def __init__(self, rd, rs1, rs2):
        super().__init__(RiscvRForm(), opcode=0b0110011, funct3=0b111, funct7=0, rd=rd, rs1=rs1, rs2=rs2)


"""
UNCONDITIONAL JUMPS
"""


# Jump And Link
class R32iJAL(RiscvInstruction):
    def __init__(self, rd, imm):
        super().__init__(RiscvJForm(), opcode=0b1101111, rd=rd, imm=imm)


# Jump And Link Register
class R32iJALR(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b1100111, funct3=0b000, rs1=rs, rd=rd, imm=imm)


"""
CONDITIONAL BRANCHES
"""


# Branch Equal
class R32iBEQ(RiscvInstruction):
    def __init__(self, rs1, rs2, imm):
        super().__init__(RiscvBForm(), opcode=0b1100011, funct3=0b000, rs1=rs1, rs2=rs2, imm=imm)


# Branch NOT Equal
class R32iBNE(RiscvInstruction):
    def __init__(self, rs1, rs2, imm):
        super().__init__(RiscvBForm(), opcode=0b1100011, funct3=0b001, rs1=rs1, rs2=rs2, imm=imm)


# Branch Less Then
class R32iBLT(RiscvInstruction):
    def __init__(self, rs1, rs2, imm):
        super().__init__(RiscvBForm(), opcode=0b1100011, funct3=0b100, rs1=rs1, rs2=rs2, imm=imm)


# Branch Greater Equal
class R32iBGE(RiscvInstruction):
    def __init__(self, rs1, rs2, imm):
        super().__init__(RiscvBForm(), opcode=0b1100011, funct3=0b101, rs1=rs1, rs2=rs2, imm=imm)


# Branch Less Then Unsigned
class R32iBLTU(RiscvInstruction):
    def __init__(self, rs1, rs2, imm):
        super().__init__(RiscvBForm(), opcode=0b1100011, funct3=0b110, rs1=rs1, rs2=rs2, imm=imm)


# Branch Greater Equal Unsigned
class R32iBGEU(RiscvInstruction):
    def __init__(self, rs1, rs2, imm):
        super().__init__(RiscvBForm(), opcode=0b1100011, funct3=0b111, rs1=rs1, rs2=rs2, imm=imm)


"""
LOAD AND STORE
"""


# Load Byte
class R32iLB(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b0000011, funct3=0b000, rd=rd, rs1=rs, imm=imm)


# Load Halfword
class R32iLH(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b0000011, funct3=0b001, rd=rd, rs1=rs, imm=imm)


# Load Word
class R32iLW(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b0000011, funct3=0b010, rd=rd, rs1=rs, imm=imm)


# Load Byte Zero Extend
class R32iLBU(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b0000011, funct3=0b100, rd=rd, rs1=rs, imm=imm)


# Load Halfword Zero Extend
class R32iLHU(RiscvInstruction):
    def __init__(self, rd, rs, imm):
        super().__init__(RiscvIForm(), opcode=0b0000011, funct3=0b101, rd=rd, rs1=rs, imm=imm)


# Store Byte
class R32iSB(RiscvInstruction):
    def __init__(self, rs, imm, ra):
        super().__init__(RiscvSForm(), opcode=0b0100011, funct3=0b000, rs1=ra, rs2=rs, imm=imm)


# Store Halfword
class R32iSH(RiscvInstruction):
    def __init__(self, rs, imm, ra):
        super().__init__(RiscvSForm(), opcode=0b0100011, funct3=0b001, rs1=ra, rs2=rs, imm=imm)


# Store Word
class R32iSW(RiscvInstruction):
    def __init__(self, rs, imm, ra):
        super().__init__(RiscvSForm(), opcode=0b0100011, funct3=0b010, rs1=ra, rs2=rs, imm=imm)


"""
FENCE
"""


class R32iFENCE(RiscvInstruction):
    def __init__(self, pi, po, pr, pw, si, so, sr, sw):
        imm = pi << 7 + po << 6 + pr << 5 + pw << 4 + si << 3 + so << 2 + sr << 1 + sw
        super().__init__(RiscvIForm(), opcode=0b0001111, funct3=0b000, rd=0, rs1=0, imm=imm)


class R32iFENCEI(RiscvInstruction):
    def __init__(self):
        super().__init__(RiscvIForm(), opcode=0b0001111, funct3=0b001, rd=0, rs1=0, imm=0)


"""
SYSTEM
"""


class R32iCSRRW(RiscvInstruction):
    def __init__(self, rd, csr, rs):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b001, rd=rd, rs1=rs, imm=csr)


class R32iCSRRS(RiscvInstruction):
    def __init__(self, rd, csr, rs):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b010, rd=rd, rs1=rs, imm=csr)


class R32iCSRRC(RiscvInstruction):
    def __init__(self, rd, csr, rs):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b011, rd=rd, rs1=rs, imm=csr)


class R32iCSRRWI(RiscvInstruction):
    def __init__(self, rd, csr, imm):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b101, rd=rd, rs1=imm, imm=csr)


class R32iCSRRSI(RiscvInstruction):
    def __init__(self, rd, csr, imm):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b110, rd=rd, rs1=imm, imm=csr)


class R32iCSRRCI(RiscvInstruction):
    def __init__(self, rd, csr, imm):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b111, rd=rd, rs1=imm, imm=csr)


"""
ENVIRONMENT
"""


class R32iECALL(RiscvInstruction):
    def __init__(self):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b000, rd=0, rs1=0, imm=0)


class R32iEBREAK(RiscvInstruction):
    def __init__(self):
        super().__init__(RiscvIForm(), opcode=0b1110011, funct3=0b000, rd=0, rs1=0, imm=1)
