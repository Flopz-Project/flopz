from enum import IntEnum

from bitstring import BitArray, Bits
from re import match

from flopz.arch.instruction import Instruction
from flopz.arch.exceptions import *
from flopz.arch.operands import BitsOperand, CombinedOperand


# used for the 32 bit unconditional branch, flips J1 and J2 (first two bits after sign) if not sign
class UB32OffsetOperand(CombinedOperand):
    def __init__(self, *args):
        super().__init__(*args, signed=True)
        assert(args[0].bits == 1)
        assert(args[1].bits == 1)
        assert(args[2].bits == 1)
        assert(args[3].bits == 10)
        assert(args[4].bits == 11)

    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # combine value from sub-operands
            res = self.operands[0]()
            sign = res[0]
            for i, op in enumerate(self.operands[1:]):
                if (i == 0 or i == 1) and not sign:
                    inverse = op()
                    inverse.invert()
                    res.append(inverse)
                else:
                    res.append(op())
            return res
        else:
            # set values in sub-operands
            power = 2 ** (self.bit_length - 1)
            arg = args[0]
            sign = arg < 0
            if arg in range(-power, power-1):
                full = BitArray(length=self.bit_length, int=arg)
                if not sign:
                    full.invert([1, 2])
                self.set_suboperators(full)

            else:
                raise InvalidArgumentRangeException(f"Invalid value {arg} for {self.bit_length}-bit signed operator")


"""
CONDITION MNEMONICS
"""


# represents mnemonics for conditionals that can return the respective 4bit code
class Cond(IntEnum):
    EQ = 0
    NE = 1
    CS = 2
    CC = 3
    MI = 4
    PL = 5
    VS = 6
    VC = 7
    HI = 8
    LS = 9
    GE = 10
    LT = 11
    GT = 12
    LE = 13
    AL = 14

    def get_bitcode(self):
        return BitArray(length=4, uint=self.value)


"""
INSTRUCTION FORMS
"""


class ThumbInstructionForm:
    def parse(self, instruction: Instruction, spec: str):
        # to be defined by subclass
        instruction.opcode_mask = BitArray(length=16, uint=0)
        instruction.opcode = lambda: BitArray([b for i, b in enumerate(instruction.bits) if instruction.opcode_mask[i]])
        pass


class ThumbInstructionForm32(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)
        instruction.opcode_mask = BitArray(length=32, uint=0)

        if not (spec[0:5] == '11101' or spec[0:4] == '1111'):
            raise Exception("Invalid opcode for 32-Bit thumb instruction")


# Shift by Immediate, move register
class ThumbInstructionFormShiftMove(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        # parse and check opcode
        if spec[0:3] != '000' or spec[3:5] == '11':
            raise Exception("Invalid opcode for Shift by immediate, move register instruction")
        instruction.opcode_mask.set(1, range(5))
        instruction.bits[0:5] = BitArray('0b' + spec[0:5])

        instruction.imm5 = BitsOperand(instruction, 5, 10)
        instruction.Rm = BitsOperand(instruction, 10, 13)
        instruction.Rd = BitsOperand(instruction, 13, 16)


# Add/subtract register
class ThumbInstructionFormASR(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        # parse and check opcode
        if spec[0:6] != '000110':
            raise Exception("Invalid opcode for Add/subtract register instruction")
        instruction.opcode_mask.set(1, range(7))
        instruction.bits[0:7] = BitArray('0b' + spec[0:7])

        instruction.Rm = BitsOperand(instruction, 7, 10)
        instruction.Rn = BitsOperand(instruction, 10, 13)
        instruction.Rd = BitsOperand(instruction, 13, 16)


# Add/subtract immediate
class ThumbInstructionFormASI(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        # parse and check opcode
        if spec[0:6] != '000111':
            raise Exception("Invalid opcode for Add/subtract immediate instruction")
        instruction.opcode_mask.set(1, range(7))
        instruction.bits[0:7] = BitArray('0b' + spec[0:7])

        instruction.imm3 = BitsOperand(instruction, 7, 10)
        instruction.Rn = BitsOperand(instruction, 10, 13)
        instruction.Rd = BitsOperand(instruction, 13, 16)


# Add/subtract/compare/move immediate
class ThumbInstructionFormASCMI(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        # parse and check opcode
        if spec[0:3] != '001':
            raise Exception("Invalid opcode for Add/subtract/compare/move immediate instruction")
        instruction.opcode_mask.set(1, range(5))
        instruction.bits[0:5] = BitArray('0b' + spec[0:5])

        instruction.Rnd = BitsOperand(instruction, 5, 8)
        instruction.imm8 = BitsOperand(instruction, 8, 16)


# Data-processing register
class ThumbInstructionFormDPR(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        # parse and check opcode
        if spec[0:6] != '010000':
            raise Exception("Invalid opcode for Data-processing register instruction")
        instruction.opcode_mask.set(1, range(10))
        instruction.bits[0:10] = BitArray('0b' + spec[0:10])

        instruction.Rm = BitsOperand(instruction, 10, 13)
        instruction.Rnd = BitsOperand(instruction, 13, 16)


# Special data processing
class ThumbInstructionFormSDP(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        # parse and check opcode
        if spec[0:6] != '010001' or spec[6:8] == '11':
            raise Exception("Invalid opcode for Special data processing instruction")
        instruction.opcode_mask.set(1, range(8))
        instruction.bits[0:8] = BitArray('0b' + spec[0:8])

        instruction.Rm = BitsOperand(instruction, 9, 13)
        instruction.Rdn = CombinedOperand(BitsOperand(instruction, 8, 9), BitsOperand(instruction, 13, 16))


# miscellaneous instruction form
class ThumbInstructionFormMISC(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:4] != '1011':
            raise Exception("Invalid opcode for MISC instruction")


# IT (if then)
class ThumbInstructionFormIT(ThumbInstructionFormMISC):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[4:8] != '1111':
            raise Exception("Invalid opcode for IT instruction")

        instruction.opcode_mask.set(1, range(8))
        instruction.bits[0:8] = BitArray('0b' + spec[0:8])

        instruction.cond = BitsOperand(instruction, 8, 12)
        instruction.mask = BitsOperand(instruction, 12, 16)


# Conditional Branch
class ThumbInstructionFormCB(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:4] != '1101' or spec[4:7] == '111':
            raise Exception("Invalid opcode or condition for conditional branch instruction")
        instruction.opcode_mask.set(1, range(4))
        instruction.bits[0:4] = BitArray('0b' + spec[0:4])

        instruction.cond = BitsOperand(instruction, 4, 8, bits=4)
        instruction.imm8 = BitsOperand(instruction, 8, 16, bits=8, signed=True)
        instruction.offset = lambda: instruction.imm8().int * 2 + 4


# Unconditional Branch
class ThumbInstructionFormUB(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:5] != '11100':
            raise Exception("Invalid opcode for unconditional branch instruction")
        instruction.opcode_mask.set(1, range(5))
        instruction.bits[0:5] = BitArray('0b' + spec[0:5])

        instruction.imm11 = BitsOperand(instruction, 5, 16, bits=11, signed=True)
        instruction.offset = lambda: instruction.imm11().int * 2 + 4


# Conditional Branch 32Bit
class ThumbInstructionFormCB32(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        instruction.opcode_mask.set(1, (0, 1, 2, 3, 4, 16, 17, 19))
        instruction.bits[0:5] = BitArray(bin='11110')
        instruction.bits[16:18] = BitArray(bin='10')
        instruction.bits[19] = 0

        instruction.encoding = CombinedOperand(BitsOperand(instruction, 5, 6, bits=1),
                                               BitsOperand(instruction, 20, 21, bits=1),
                                               BitsOperand(instruction, 18, 19, bits=1),
                                               BitsOperand(instruction, 10, 16, bits=6),
                                               BitsOperand(instruction, 21, 32, bits=11), signed=True)
        instruction.cond = BitsOperand(instruction, 6, 10)

        instruction.offset = lambda: instruction.encoding().int * 2 + 4


# Unconditional Branch 32Bit
class ThumbInstructionFormUB32(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        instruction.opcode_mask.set(1, (0, 1, 2, 3, 4, 16, 17, 19))
        instruction.bits[0:5]  = BitArray(bin='11110')
        instruction.bits[16:18] = BitArray(bin='10')
        instruction.bits[19] = 1

        instruction.encoding = UB32OffsetOperand(BitsOperand(instruction, 5, 6, bits=1),
                                                 BitsOperand(instruction, 18, 19, bits=1),
                                                 BitsOperand(instruction, 20, 21, bits=1),
                                                 BitsOperand(instruction, 6, 16, bits=10),
                                                 BitsOperand(instruction, 21, 32, bits=11))

        instruction.offset = lambda: instruction.encoding().int * 2 + 4


# store/load immediate 16Bit
class ThumbInstructionFormSLI(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:3] != '011':
            raise Exception("Invalid opcode for store/load immediate instruction")

        instruction.opcode_mask.set(1, range(5))
        instruction.bits[0:5] = BitArray('0b' + spec[0:5])

        instruction.imm5 = BitsOperand(instruction, 5, 10, bits=5)
        instruction.Rn = BitsOperand(instruction, 10, 13, bits=3)
        instruction.Rt = BitsOperand(instruction, 13, 16, bits=3)

        instruction.Bytemode = BitsOperand(instruction, 3, 4, bits=1)


# store/load halfword 16Bit
class ThumbinstructionFormSLIHW(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:4] != '1000':
            raise Exception("Invalid opcode for store/load hw instruction")

        instruction.opcode_mask.set(1, range(6))
        instruction.bits[0:5] = BitArray('0b' + spec[0:5])

        instruction.imm5 = BitsOperand(instruction, 5, 10, bits=5)
        instruction.Rn = BitsOperand(instruction, 10, 13, bits=3)
        instruction.Rt = BitsOperand(instruction, 13, 16, bits=3)


# store/load immediate 32Bit
class ThumbInstructionFormStrLdrImmT4(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:5] != '11111':
            raise Exception("Invalid opcode for store/load immediate 32Bit instruction")

        instruction.opcode_mask.set(1, range(12))
        instruction.opcode_mask.set(1, 20)
        instruction.bits[0:12] = BitArray('0b' + spec[0:12])
        instruction.bits[20:21] = BitArray('0b' + spec[spec.find('P') - 1:spec.find('P')])

        instruction.Rn = BitsOperand(instruction, 12, 16, bits=4)
        instruction.Rt = BitsOperand(instruction, 16, 20, bits=4)

        instruction.P = BitsOperand(instruction, 21, 22)
        instruction.U = BitsOperand(instruction, 22, 23)
        instruction.W = BitsOperand(instruction, 23, 24)

        instruction.imm8 = BitsOperand(instruction, 24, 32, bits=8)

        instruction.Wordmode = BitsOperand(instruction, 9, 11, bits=2)


# store/load register 32Bit
class ThumbinstructionFormStrLdrRegT2(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:5] != '11111':
            raise Exception("Invalid opcode for store/load register 32Bit instruction")

        instruction.opcode_mask.set(1, range(12))
        instruction.opcode_mask.set(1, 20)
        instruction.bits[0:12] = BitArray('0b' + spec[0:12])
        instruction.bits[20:26] = BitArray(bin='000000')

        instruction.Rn = BitsOperand(instruction, 12, 16, bits=4)
        instruction.Rt = BitsOperand(instruction, 16, 20, bits=4)

        instruction.shift = BitsOperand(instruction, 26, 28, bits=2)
        instruction.Rm = BitsOperand(instruction, 28, 32, bits=4)

        instruction.Wordmode = BitsOperand(instruction, 9, 11, bits=2)


# store/load immediate 32Bit with 12Bit immediate
class ThumbInstructionFormStrLdrT3(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:5] != '11111':
            raise Exception("Invalid opcode for store/load immediate 32Bit instruction")

        instruction.opcode_mask.set(1, range(12))
        instruction.bits[0:12] = BitArray('0b' + spec[0:12])

        instruction.Rn = BitsOperand(instruction, 12, 16, bits=4)
        instruction.Rt = BitsOperand(instruction, 16, 20, bits=4)
        instruction.imm12 = BitsOperand(instruction, 20, 32, bits=12)

        instruction.Wordmode = BitsOperand(instruction, 9, 11, bits=2)


# load literal 32Bit
class ThumbInstructionFormLdrL32(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:5] != '11111':
            raise Exception("Invalid opcode for load literal 32Bit instruction")

        instruction.opcode_mask.set(1, range(16))
        instruction.opcode_mask.set(0, 8)
        instruction.bits[0:8] = BitArray('0b' + spec[0:8])
        instruction.bits[9:16] = BitArray('0b' + spec[9:16])

        instruction.U = BitsOperand(instruction, 8, 9, bits=1)
        instruction.Rt = BitsOperand(instruction, 16, 20, bits=4)
        instruction.imm12 = BitsOperand(instruction, 20, 32, bits=12)


# store / load multiple 16Bit
class ThumbInstructionFormStmiaLdmia(ThumbInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        if spec[0:4] != '1100':
            raise Exception("Invalid opcode for load store multiple 16Bit instruction")

        instruction.opcode_mask.set(1, range(5))
        instruction.bits[0:5] = BitArray('0b' + spec[0:5])

        instruction.Rn = BitsOperand(instruction, 5, 8, bits=3)
        instruction.register_list = BitsOperand(instruction, 8, 16, bits=8)


# store / load multiple 32Bit
class ThumbInstructionFormStmiaLdmiaW(ThumbInstructionForm32):
    def parse(self, instruction: Instruction, spec: str):
        super().parse(instruction, spec)

        instruction.opcode_mask.set(1, range(12))
        instruction.bits[0:10] = BitArray('0b' + spec[0:10])
        instruction.bits[11:12] = BitArray('0b' + spec[11:12])
        instruction.bits[18:19] = BitArray(bin='0')

        instruction.W = BitsOperand(instruction, 10, 11, bits=1)
        instruction.Rn = BitsOperand(instruction, 12, 16)
        instruction.register_list = BitsOperand(instruction, 16, 32, bits=16)


"""
INSTRUCTIONS
"""


class ThumbInstruction(Instruction):
    def __init__(self, form: ThumbInstructionForm, spec: str, addr: int = 0, bit_length=16, **kwargs):
        # check for 32 bit form
        if issubclass(type(form), ThumbInstructionForm32):
            bit_length = 32

        super().__init__(spec, addr, bit_length)

        # sanitize spec
        self.spec = spec.upper().replace(' ', '')
        self.instruction_form = form
        self.instruction_form.parse(self, self.spec)

        # apply the operands using kwargs
        for k, v in kwargs.items():
            operand = getattr(self, k)
            operand(v)

    def bytes(self) -> bytes:
        swapped_bits = self.bits.copy()
        # 16 bit thumb instructions show up with LSB first (little endian)
        if self.bit_length == 16:
            swapped_bits.byteswap(2)
        else:
            # 32 bit thumb2 instructions are 2 halfwords with little endian
            swapped_bits.byteswap(2)
        return swapped_bits.bytes


"""
ARITHMETIC
"""


# ADD (immediate)
class AddsI(ThumbInstruction):
    def __init__(self, rd, rn, im3):
        super().__init__(form=ThumbInstructionFormASI(), spec='0 0 0 1 1 1 0 imm3 Rn Rd', Rn=rn, Rd=rd, imm3=im3)


# SUB (immediate)
class SubsI(ThumbInstruction):
    def __init__(self, rd, rn, im3):
        super().__init__(form=ThumbInstructionFormASI(), spec='0 0 0 1 1 1 1 imm3 Rn Rd', Rn=rn, Rd=rd, imm3=im3)


# ADD (register)
class AddsR(ThumbInstruction):
    def __init__(self, rd, rn, rm):
        super().__init__(form=ThumbInstructionFormASR(), spec='0 0 0 1 1 0 0 Rm Rn Rd', Rm=rm, Rn=rn, Rd=rd)


# SUB (register)
class SubsR(ThumbInstruction):
    def __init__(self, rd, rn, rm):
        super().__init__(form=ThumbInstructionFormASR(), spec='0 0 0 1 1 0 1 Rm Rn Rd', Rm=rm, Rn=rn, Rd=rd)


"""
MOVE AND SHIFTS
"""


# MOV (register) NO TEST
class MovT2(ThumbInstruction):
    def __init__(self, rd, rm):
        super().__init__(form=ThumbInstructionFormShiftMove(), spec='0 0 0 0 0 0 0 0 0 0 Rm Rd', Rm=rm, Rd=rd, imm5=0)


class MovT1(ThumbInstruction):
    def __init__(self, rd, rm):
        super().__init__(form=ThumbInstructionFormSDP(), spec='0 1 0 0 0 1 1 0 D Rm Rd', Rm=rm, Rdn=rd)


# LSL (immediate)
class LslsI(ThumbInstruction):
    def __init__(self, rd, rm, im5):
        super().__init__(form=ThumbInstructionFormShiftMove(), spec='0 0 0 0 0 imm5 Rm Rd', imm5=im5, Rm=rm, Rd=rd)


# LSR (immediate)
class LsrsI(ThumbInstruction):
    def __init__(self, rd, rm, im5):
        super().__init__(form=ThumbInstructionFormShiftMove(), spec='0 0 0 0 1 imm5 Rm Rd', imm5=im5, Rm=rm, Rd=rd)


# ASR (immediate) NO TEST
class AsrI(ThumbInstruction):
    def __init__(self, rd, rm, im5):
        super().__init__(form=ThumbInstructionFormShiftMove(), spec='0 0 0 1 0 imm5 Rm Rd', imm5=im5, Rm=rm, Rd=rd)


"""
IT
"""


# IT (if then)
class IT(ThumbInstruction):
    def __init__(self, cond: Cond, mask: str):
        # check mask validity
        if match('[ET]{0,3}', mask) is None:
            raise InvalidArgumentException(f"{mask} is an invalid mask expression (use T for then, E for else)")
        if len(mask) > 3:
            raise InvalidArgumentException(f"{mask} is too long for a valid mask expression (max len is 3)")

        # parse mask
        cond_lsb = cond.get_bitcode()[3]
        bit_mask = 1 << (3 - len(mask))

        for i, c in enumerate(mask):
            if c == 'T':
                bit_mask += cond_lsb << (3-i)
            elif c == 'E':
                bit_mask += (cond_lsb+1) % 2 << (3-i)

        super().__init__(form=ThumbInstructionFormIT(), spec='1 0 1 1 1 1 1 1 firstcond mask', cond=cond, mask=bit_mask)


"""
BRANCHES
"""


# CB (conditional branch)
class CB(ThumbInstruction):
    def __init__(self, cond: Cond, offset):
        if offset not in range(-252, 259) or offset % 2 != 0:  # shift range +4 due to PC label offset of 4 for thumb
            raise InvalidArgumentRangeException("Offset out of range for this CB")
        super().__init__(form=ThumbInstructionFormCB(), spec='1 1 0 1 cond imm8', cond=cond, imm8=(offset - 4) >> 1)


# UB (unconditional branch) NO TEST
class UB(ThumbInstruction):
    def __init__(self, offset):
        if offset not in range(-2044, 2051) or offset % 2 != 0:
            raise InvalidArgumentRangeException(f"Offset out of range for this UB")
        super().__init__(form=ThumbInstructionFormUB(), spec='1 1 1 0 0 imm11', imm11=(offset - 4) >> 1)


# CB32 (conditional branch 32bit)
class CBW(ThumbInstruction):
    def __init__(self, cond: Cond, offset):
        if offset not in range(-1048572, 1048579) or offset % 2 != 0:
            raise InvalidArgumentRangeException(f"Offset {offset} out of range for 32 Bit CB")
        super().__init__(form=ThumbInstructionFormCB32(), spec='1 1 1 1 0 S cond imm6 1 0 J1 0 J2 imm11', bit_length=32,
                         cond=cond, encoding=(offset - 4) >> 1)


# UB32 (unconditional branch 32bit)
class UBW(ThumbInstruction):
    def __init__(self, offset):
        if offset not in range(-16777212, 16777219) or offset % 2 != 0:
            raise InvalidArgumentRangeException(f"Offset {offset} out of range for 32 Bit UB")
        super().__init__(form=ThumbInstructionFormUB32(), spec='1 1 1 1 0 S imm10 1 0 J1 1 J2 imm11 ', bit_length=32,
                         encoding=(offset - 4) >> 1)


"""
STORES/LOADS
"""


# store (immediate)
class StrI(ThumbInstruction):
    def __init__(self, rt, rn, offset=0, byte=False):
        if offset % 4 != 0 or offset not in range(125):
            raise InvalidArgumentRangeException("Invalid offset for this store encoding")
        if rn not in range(8) or rt not in range(8):
            raise InvalidArgumentRangeException("Invalid register for this store encoding")
        if not byte:
            super().__init__(form=ThumbInstructionFormSLI(), spec='0 1 1 0 0 imm5 Rn Rt', Rt=rt, Rn=rn,
                             imm5=(offset >> 2))
        else:
            super().__init__(form=ThumbInstructionFormSLI(), spec='0 1 1 1 0 imm5 Rn Rt', Rt=rt, Rn=rn,
                             imm5=(offset >> 2))


# store halfword (immediate)
class StrIHw(ThumbInstruction):
    def __init__(self, rt, rn, offset=0):
        if offset % 2 != 0 or offset not in range(64):
            raise InvalidArgumentRangeException("Invalid offset for this store encoding")
        if rn not in range(8) or rt not in range(8):
            raise InvalidArgumentRangeException("Invalid register for this store encoding")
        super().__init__(form=ThumbinstructionFormSLIHW(), spec='1 0 0 0 0 imm5 Rn Rt', Rt=rt, Rn=rn,
                         imm5=(offset >> 1))


# store32 (immediate)
class StrWI(ThumbInstruction):
    def __init__(self, rt, rn, offset=0, index=True, wback=False, byte=False, hword=False):
        if offset not in range(-255, 256):
            raise InvalidArgumentRangeException("Invalid offset for this store encoding")
        if rn not in range(16) or rt not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        if byte and hword:
            raise InvalidFlagCombinationException("Instruction can't simultaneously encode bytemode and halfwordmode")

        super().__init__(form=ThumbInstructionFormStrLdrImmT4(), spec='1 1 1 1 1 0 0 0 0 1 0 0 Rn Rt 1 P U W imm8',
                         Rt=rt, Rn=rn, imm8=abs(offset), P=index, U=(offset >= 0), W=wback, bit_length=32)
        if byte:
            self.Wordmode(0)
        elif hword:
            self.Wordmode(1)


# store32 (long immediate)
class StrWI12(ThumbInstruction):
    def __init__(self, rt, rn, offset=0, byte=False, hword=False):
        if offset not in range(4096):
            raise InvalidArgumentRangeException("Invalid offset for this store encoding")
        if rn not in range(16) or rt not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        if byte and hword:
            raise InvalidFlagCombinationException("Instruction can't simultaneously encode bytemode and halfwordmode")
        super().__init__(form=ThumbInstructionFormStrLdrT3(), spec='1 1 1 1 1 0 0 0 1 1 0 0 Rn Rt imm12',
                         Rt=rt, Rn=rn, imm12=offset)
        if byte:
            self.Wordmode(0)
        elif hword:
            self.Wordmode(1)


# store32 (register)
class StrWR(ThumbInstruction):
    def __init__(self, rt, rn, rm, shift=0, byte=False, hword=False):
        if rn not in range(16) or rt not in range(16) or rm not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        if shift not in range(4):
            raise InvalidArgumentRangeException("Invalid shift")
        if byte and hword:
            raise InvalidFlagCombinationException("Instruction can't simultaneously encode bytemode and halfwordmode")
        super().__init__(form=ThumbinstructionFormStrLdrRegT2(),
                         spec='1 1 1 1 1 0 0 0 0 1 0 0 Rn Rt 0 0 0 0 0 0 shift Rm', Rt=rt, Rn=rn, Rm=rm, shift=shift)
        if byte:
            self.Wordmode(0)
        elif hword:
            self.Wordmode(1)


# load (immediate)
class LdrI(ThumbInstruction):
    def __init__(self, rt, rn, offset=0, byte=False):
        if offset % 4 != 0 or offset not in range(125):
            raise InvalidArgumentRangeException("Invalid offset for this load encoding")
        if rn not in range(8) or rt not in range(8):
            raise InvalidArgumentRangeException("Invalid register for this load encoding")
        if not byte:
            super().__init__(form=ThumbInstructionFormSLI(), spec='0 1 1 0 1 imm5 Rn Rt', Rt=rt, Rn=rn,
                             imm5=(offset >> 2))
        else:
            super().__init__(form=ThumbInstructionFormSLI(), spec='0 1 1 1 1 imm5 Rn Rt', Rt=rt, Rn=rn,
                             imm5=(offset >> 2))


# load halfword (immediate)
class LdrIHw(ThumbInstruction):
    def __init__(self, rt, rn, offset=0):
        if offset % 2 != 0 or offset not in range(64):
            raise InvalidArgumentRangeException("Invalid offset for this store encoding")
        if rn not in range(8) or rt not in range(8):
            raise InvalidArgumentRangeException("Invalid register for this store encoding")
        super().__init__(form=ThumbinstructionFormSLIHW(), spec='1 0 0 0 1 imm5 Rn Rt', Rt=rt, Rn=rn,
                         imm5=(offset >> 1))


# load32 (immediate) NO TEST
class LdrWI(ThumbInstruction):
    def __init__(self, rt, rn, offset=0, index=True, wback=False, byte=False, hword=False):
        if offset not in range(-255, 256):
            raise InvalidArgumentRangeException("Invalid offset for this load encoding")
        if rn not in range(16) or rt not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        if byte and hword:
            raise InvalidFlagCombinationException("Instruction can't simultaneously encode bytemode and halfwordmode")
        super().__init__(form=ThumbInstructionFormStrLdrImmT4(), spec='1 1 1 1 1 0 0 0 0 1 0 1 Rn Rt 1 P U W imm8',
                         Rt=rt, Rn=rn, imm8=abs(offset), P=index, U=(offset >= 0), W=wback, bit_length=32)
        if byte:
            self.Wordmode(0)
        elif hword:
            self.Wordmode(1)


# load32 (long immediate)
class LdrWI12(ThumbInstruction):
    def __init__(self, rt, rn, offset=0, byte=False, hword=False):
        if offset not in range(4096):
            raise InvalidArgumentRangeException("Invalid offset for this load encoding")
        if rn not in range(16) or rt not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        if byte and hword:
            raise InvalidFlagCombinationException("Instruction can't simultaneously encode bytemode and halfwordmode")
        super().__init__(form=ThumbInstructionFormStrLdrT3(), spec='1 1 1 1 1 0 0 0 1 1 0 1 Rn Rt imm12',
                         Rt=rt, Rn=rn, imm12=offset)
        if byte:
            self.Wordmode(0)
        elif hword:
            self.Wordmode(1)


# load32 (literal)
class LdrWLit(ThumbInstruction):
    def __init__(self, rt, offset):
        if offset not in range(-4095, 4096):
            raise InvalidArgumentRangeException("Invalid offset for this load literal encoding")
        if rt not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        super().__init__(form=ThumbInstructionFormLdrL32(), spec='1 1 1 1 1 0 0 0 U 1 0 1 1 1 1 1 Rt imm12', Rt=rt,
                         U=(offset >= 0), imm12=abs(offset))


# load32 (register)
class LdrWR(ThumbInstruction):
    def __init__(self, rt, rn, rm, shift=0, byte=False, hword=False):
        if rn not in range(16) or rt not in range(16) or rm not in range(16):
            raise InvalidArgumentRangeException("Invalid register")
        if shift not in range(4):
            raise InvalidArgumentRangeException("Invalid shift")
        if byte and hword:
            raise InvalidFlagCombinationException("Instruction can't simultaneously encode bytemode and halfwordmode")
        super().__init__(form=ThumbinstructionFormStrLdrRegT2(),
                         spec='1 1 1 1 1 0 0 0 0 1 0 1 Rn Rt 0 0 0 0 0 0 shift Rm', Rt=rt, Rn=rn, Rm=rm, shift=shift)
        if byte:
            self.Wordmode(0)
        elif hword:
            self.Wordmode(1)


"""
STORE / LOAD MULTIPLE
"""


# store multiple 16Bit
class Stmia(ThumbInstruction):
    def __init__(self, rn: int, register_list: [int]):
        if rn not in range(8):
            raise InvalidArgumentRangeException("Invalid register for 16Bit store multiple instruction")
        if any([r not in range(8) for r in register_list]):
            raise InvalidArgumentRangeException("Invalid register in register list")
        rlist_bitencoding = 0
        for r in register_list:
            rlist_bitencoding += 1 << r
        super().__init__(form=ThumbInstructionFormStmiaLdmia(), spec='1 1 0 0 0 Rn register_list',
                         Rn=rn, register_list=rlist_bitencoding)


# load multiple 16Bit
class Ldmia(ThumbInstruction):
    def __init__(self, rn: int, register_list: [int]):
        if rn not in range(8):
            raise InvalidArgumentRangeException("Invalid register for 16Bit load multiple instruction")
        if any([r not in range(8) for r in register_list]):
            raise InvalidArgumentRangeException("Invalid register in register list")
        rlist_bitencoding = 0
        for r in register_list:
            rlist_bitencoding += 1 << r
        super().__init__(form=ThumbInstructionFormStmiaLdmia(), spec='1 1 0 0 1 Rn register_list',
                         Rn=rn, register_list=rlist_bitencoding)

# store multiple 32Bit
class StmiaW(ThumbInstruction):
    def __init__(self, rn: int, register_list: [int], wback: bool = False):
        if rn not in range(15):
            raise InvalidArgumentRangeException("Invalid register for 32Bit store multiple instruction")
        if any([r not in range(13) and r != 14 for r in register_list]):
            raise InvalidArgumentRangeException("Invalid register in register list")
        rlist_bitencoding = 0
        for r in register_list:
            rlist_bitencoding += 1 << r

        super().__init__(form=ThumbInstructionFormStmiaLdmiaW(),
                         spec='1 1 1 0 1 0 0 0 1 0 W 0 Rn (0) M (0) register_list',
                         Rn=rn, register_list=rlist_bitencoding, W=wback)


# load multiple 32Bit
class LdmiaW(ThumbInstruction):
    def __init__(self, rn: int, register_list: [int], wback: bool = False):
        if rn not in range(15):
            raise InvalidArgumentRangeException("Invalid register for 32Bit load multiple instruction")
        if any([r not in range(13) and r != 14 and r != 15 for r in register_list]):
            raise InvalidArgumentRangeException("Invalid register in register list")
        rlist_bitencoding = 0
        for r in register_list:
            rlist_bitencoding += 1 << r

        super().__init__(form=ThumbInstructionFormStmiaLdmiaW(),
                         spec='1 1 1 0 1 0 0 0 1 0 W 1 Rn P M (0) register_list',
                         Rn=rn, register_list=rlist_bitencoding, W=wback)
