import enum

from bitstring import BitArray, Bits
from re import match

from flopz.arch.instruction import Instruction
from flopz.arch.operands import Operand


class VleInstructionForm:
    def parse(self, instruction: Instruction, spec: str):
        # to be defined by subclass
        pass

class Bo16FieldEncodings(enum.IntEnum):
    # For 16-bit instructions using BI16, only CR[32–35] (bits within CR0) may be specified.
    BranchIfConditionIsFalse = 0
    BranchIfConditionIsTrue = 1

class RdOperand(Operand):
    # full 5 bit register operand (GP r0 - r31)
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(RdOperand, self).__call__()
        else:
            # set!
            reg_val = self._get_register(args[0])
            if reg_val in range(0,32):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = reg_val
            else:
                raise Exception("Invalid range for RdOperand!")

class RxyaOperand(Operand):
    # need to encode the values as defined in VLE spec (4 bits!)
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(RxyaOperand, self).__call__()
        else:
            # set!
            reg_val = self._get_register(args[0])
            if reg_val <= 7:
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = reg_val
            elif reg_val in range(24,32):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = (8 | (reg_val - 24))
            else:
                raise Exception("Invalid range for RxyaOperand!")


class ARxyaOperand(Operand):
    # need to encode the values as defined in VLE spec (arx is from r8 - r23)
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(ARxyaOperand, self).__call__()
        else:
            # set!
            reg_val = self._get_register(args[0])
            if reg_val in range(8,24):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = reg_val - 8
            else:
                raise Exception("ARX operand: register is out of range [r8 - r23]")

class OIM5Operand(Operand):
    # Offset Immediate field used to specify a 5-bit unsigned Integer value in the range [1:32] encoded as [0:31]. Thus
    # the binary encoding of 00000 represents an immediate value of 1, 00001 represents an immediate value of 2,
    # and so on.
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return Bits(int=super(OIM5Operand, self).__call__().int + 1, length=5)
        else:
            # set!
            if args[0] in range(1,32):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = args[0] - 1
            else:
                raise Exception("OIM5 operand: immediate is out of range [1 - 32]")


class UI5Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return Bits(uint=super(UI5Operand, self).__call__().uint, length=5)
        else:
            # set!
            if args[0] in range(0,32):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = args[0]
            else:
                raise Exception("OIM5 operand: immediate is out of range [0 - 32]")

class BD24Operand(Operand):
    # (Used by 32-bit branch class instructions) A 24-bit signed displacement, sign-extended and shifted left
    # one bit (concatenated with 0) and added to the current instruction address to form the branch target
    # address.
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(BD24Operand, self).__call__()
        else:
            # set!
            if args[0] in range(-0xffffff, 0x1000000):
                # right-shift one bit, make sure that lsb is 0
                if args[0] & 0x1:
                    raise Exception('LSB of BD Operand needs to be 0!')

                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(int=(args[0] >> 1), length=24)
            else:
                raise Exception("OIM5 operand: immediate is out of range [1 - 32]")

class BD15Operand(Operand):
    # (Used by 32-bit branch conditional class instructions) A 15-bit signed displacement sign-extended and
    # shifted left one bit (concatenated with 0) and added to the current instruction address to form the branch
    # target address.
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(BD15Operand, self).__call__()
        else:
            # set!
            if args[0] in range(-0xffff, 0x10000):
                # right-shift one bit, make sure that lsb is 0
                if args[0] & 0x1:
                    raise Exception('LSB of BD Operand needs to be 0!')

                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(int=(args[0] >> 1), length=15)
            else:
                raise Exception("OIM5 operand: immediate is out of range [1 - 32]")

class BD8Operand(Operand):
    # (Used by 16-bit branch and branch conditional class instructions) An 8-bit signed displacement
    # sign-extended and shifted left one bit (concatenated with 0) and added to the current instruction address
    # to form the branch target address.
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(BD8Operand, self).__call__()
        else:
            # set!
            if args[0] in range(-0xff, 0x100):
                # right-shift one bit, make sure that lsb is 0
                if args[0] & 0x1:
                    raise Exception('LSB of BD Operand needs to be 0!')

                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(int=(args[0] >> 1), length=8)
            else:
                raise Exception("OIM5 operand: immediate is out of range [1 - 32]")

class D16Operand(Operand):
    # Used by 32 bit store operations
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(D16Operand, self).__call__()
        else:
            # set!
            if args[0] in range(-0x8000, 0x8000):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(int=(args[0]), length=16)
            else:
                raise Exception("D16Operand operand: immediate is out of range [-0x8000 - 0x8000]")

class D8Operand(Operand):
    # Used by e_stmw
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get: we don't change anything
            return super(D8Operand, self).__call__()
        else:
            # set!
            if args[0] in range(-0x80, 0x80):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(int=(args[0]), length=8)
            else:
                raise Exception("D8Operand operand: immediate is out of range [-0x80 - 0x80]")

class I20Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # assume bitpos start points to lowest bit in instruction from which I20 starts
            # layout: LI20[4:8] | 0  | LI20[0:3] | LI20[9:19]
            pos = self.bitpos_start
            i20_4_8 = self.instruction.bits[pos:pos+5]
            pos += 6 # skip in-between bit
            i20_0_3 = self.instruction.bits[pos:pos+4]
            pos += 4
            i20_9_19 = self.instruction.bits[pos:pos+11]
            sprn = i20_0_3 + i20_4_8 + i20_9_19
            return sprn
        else:
            # set!
            if args[0] in range(-0x7ffff, 0x80000):
                val = Bits(int=args[0], length=20)
                pos = self.bitpos_start
                self.instruction.bits[pos:pos + 5] = val[4:9]
                pos += 6  # skip in-between bit
                self.instruction.bits[pos:pos + 4] = val[0:4]
                pos += 4
                self.instruction.bits[pos:pos + 11] = val[9:20]
            else:
                raise Exception("I20Operand: I20 is out of range [-0x7ffff - 0x80000]")

class UI16Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # assume bitpos start points to lowest bit in instruction from which UI16 starts
            # layout: UI[0:4] | x x x x x | UI[5:15]

            ui_0_4 = self.instruction.bits[self.bitpos_start:self.bitpos_start+5]
            ui_5_15 = self.instruction.bits[self.bitpos_start+10:]
            ui = ui_0_4 + ui_5_15
            return ui
        else:
            # set!
            if args[0] in range(0, 0xffff):
                val = Bits(uint=args[0], length=16)
                self.instruction.bits[self.bitpos_start:self.bitpos_start+5] = val[:5]
                self.instruction.bits[self.bitpos_start+10:] = val[5:]
            else:
                raise Exception("UI16Operand: Immediate is out of range [0 - 0xffff]")

class SI16Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # assume bitpos start points to lowest bit in instruction from which SI16 starts
            # layout: SI[0:4] | x x x x x | x x x x x | SI[5:15]
            si_0_4 = self.instruction.bits[self.bitpos_start:self.bitpos_start+5]
            si_5_15 = self.instruction.bits[self.bitpos_start+15:]
            si = si_0_4 + si_5_15
            return si
        else:
            # set!
            if args[0] in range(-0x7fff, 0x8000):
                val = Bits(int=args[0], length=16)
                self.instruction.bits[self.bitpos_start:self.bitpos_start+5] = val[:5]
                self.instruction.bits[self.bitpos_start+15:] = val[5:]
            else:
                raise Exception("SI16Operand: Immediate is out of range [-0x7fff - 0x7fff]")


class UI7Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start:self.bitpos_end]
        else:
            # set!
            if args[0] in range(0, 0x80):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(uint=args[0], length=7)
            else:
                raise Exception("UI7Operand: Immediate is out of range [0 - 0x80]")


class UI8Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start:self.bitpos_end]
        else:
            # set!
            if args[0] in range(0, 0x100):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(uint=args[0], length=8)
            else:
                raise Exception("UI8Operand: Immediate is out of range [0 - 0xff]")

class SD4Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start:self.bitpos_end]
        else:
            # set!
            if args[0] in range(0, 0x10):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(uint=args[0], length=4)
            else:
                raise Exception("SD4Operand: Immediate is out of range [0 - 0x10)")

class SD4LS1Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start:self.bitpos_end] << 1
        else:
            # set!
            if args[0] in range(0, 0x20) or (args[0] % 2 != 0):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(uint=(args[0] >> 1), length=4)
            else:
                raise Exception("SD4Operand: Immediate is out of range [0 - 0x20) or not halfword-aligned!")


class SD4LS2Operand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start:self.bitpos_end] << 2
        else:
            # set!
            if args[0] in range(0, 0x40) or (args[0] % 4 != 0):
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = Bits(uint=(args[0] >> 2), length=4)
            else:
                raise Exception("SD4Operand: Immediate is out of range [0 - 0x40) or not word-aligned!")

class SIOperand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # just like UI16, except that this value is sign-extended
            si_0_4 = self.instruction.bits[self.bitpos_start:self.bitpos_start+5]
            si_5_15 = self.instruction.bits[self.bitpos_start+10:]
            si = si_0_4 + si_5_15
            return si
        else:
            # set!
            if args[0] in range(-0x7fff, 0x8000):
                val = Bits(int=args[0], length=16)
                self.instruction.bits[self.bitpos_start:self.bitpos_start+5] = val[:5]
                self.instruction.bits[self.bitpos_start+10:] = val[5:]
            else:
                raise Exception("I20Operand: SPRN is out of range [0 - 0xffff]")

class SPRNOperand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # layout: SPRN[5–9] | SPRN[ 0–4]
            sprn59 = self.instruction.bits[self.bitpos_start:self.bitpos_start+5]
            sprn04 = self.instruction.bits[self.bitpos_start+5:self.bitpos_end]
            sprn = sprn04 + sprn59
            return sprn
        else:
            # set!
            if args[0] in range(0, 0x3ff):
                val = Bits(uint=args[0], length=10)
                sprn59 = val[5:]
                sprn04 = val[:5]
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = sprn59 + sprn04
            else:
                raise Exception("SPRNOperand: SPRN is out of range [0 - 0x3ff]")


class CRMOperand(Operand):
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            crm = self.instruction.bits[self.bitpos_start:self.bitpos_start+8]
            return crm
        else:
            # set!
            if args[0] in range(0, 0x100):
                val = Bits(uint=args[0], length=8)
                self.instruction.bits[self.bitpos_start:self.bitpos_end] = val
            else:
                raise Exception("CRMOperand: CRM is out of range [0 - 0x100]")

class SingleBitOperand(Operand):
    # only uses bitpos_start to determine which bit to use
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start]
        else:
            # set!
            self.instruction.bits[self.bitpos_start] = Bits(bin=str(args[0]))


class DualBitOperand(Operand):
    # only uses bitpos_start to determine which bits to use
    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            return self.instruction.bits[self.bitpos_start:self.bitpos_start+2]
        else:
            # set!
            self.instruction.bits[self.bitpos_start:self.bitpos_start+2] = Bits(uint=args[0], length=2)


class VleInstructionFormRR(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormRR, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        # parse the following stuff
        bitpos = 6
        fmt_pos = 0
        lean_format = spec[6:]

        while True:
            c = lean_format[fmt_pos]
            if c == '0':
                instruction.bits[bitpos] = 0
                bitpos += 1
                fmt_pos += 1
            elif c == '1':
                instruction.bits[bitpos] = 1
                bitpos += 1
                fmt_pos += 1
            else:
                # check if at end or operand
                if len(lean_format[fmt_pos:]) >= 2:
                    # match operand
                    if match('R[XYA]', lean_format[fmt_pos:fmt_pos + 2]):
                        # gp register, encoded with 4 bits in 16 bit instructions
                        if instruction.bit_length == 16:
                            setattr(instruction, lean_format[fmt_pos:fmt_pos + 2],
                                    RxyaOperand(instruction, bitpos, bitpos + 4))
                            bitpos += 4
                            fmt_pos += 2
                        else:
                            raise Exception("RR Format 32 bit: invalid!")
                    if match('AR[XYA]', lean_format[fmt_pos:fmt_pos+3]):
                        # AR* operand encoded with 4 bits
                        if instruction.bit_length == 16:
                            setattr(instruction, lean_format[fmt_pos:fmt_pos + 3],
                                    ARxyaOperand(instruction, bitpos, bitpos + 4))
                            bitpos += 4
                            fmt_pos += 3
                        else:
                            raise Exception("RR Format 32 bit: invalid!")
                else:
                    # unknown case, error
                    raise Exception("Error parsing RR format!")

            if len(lean_format) <= fmt_pos:
                break  # done

class VleInstructionFormR(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormIM5, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:12])
        instruction.bits[0:12] = instruction.opcode
        instruction.RX = RxyaOperand(instruction, 12, 16)

class VleInstructionFormIM5(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormIM5, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:7])
        instruction.bits[0:7] = instruction.opcode

        instruction.UI5 = UI5Operand(instruction, 7, 12)
        instruction.RX = RxyaOperand(instruction, 12, 16)

class VleInstructionFormOIM5(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormOIM5, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        # parse the following stuff
        bitpos = 6
        lean_format = spec[6:]

        instruction.xo_rc = lean_format[0]
        instruction.bits[bitpos] = 1 if (instruction.xo_rc == '1') else 0
        bitpos += 1

        instruction.OIM5 = OIM5Operand(instruction, bitpos, bitpos + 5)
        bitpos += 5
        instruction.RX = RxyaOperand(instruction, bitpos, bitpos + 4)

class VleInstructionFormBD24(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormBD24, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        # parse the following stuff
        bitpos = 6
        lean_format = spec[6:]

        #instruction.bits[bitpos] = 1 if (instruction.xo_rc == '1') else 0
        if lean_format[0] == '0':
            instruction.bits[bitpos] = 0
        else:
            raise Exception("invalid pos 6 for BD24-type instruction!")
        bitpos += 1

        instruction.BD24 = BD24Operand(instruction, bitpos, bitpos + 24)
        instruction.LK = 1 if lean_format[-1] == '1' else 0
        instruction.bits[31] = instruction.LK

class VleInstructionFormBD15(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormBD15, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        # parse the following stuff
        bitpos = 6
        lean_format = spec[6:]

        if lean_format[0] == '0':
            instruction.bits[bitpos] = 0
        else:
            raise Exception("invalid pos 6 for BD24-type instruction!")
        bitpos += 1

        instruction.BD15 = BD15Operand(instruction, bitpos, bitpos + 15)
        instruction.LK = 1 if lean_format[-1] == '1' else 0
        instruction.bits[31] = instruction.LK

class VleInstructionFormBD8(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormBD8, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = BitArray('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        # parse the following stuff
        bitpos = 6
        lean_format = spec[6:]

        if lean_format[0] == '0':
            instruction.bits[bitpos] = 0
        else:
            raise Exception("invalid pos 6 for BD24-type instruction!")

        instruction.LK = 1 if lean_format[1] == '1' else 0
        bitpos = 7
        instruction.bits[bitpos] = instruction.LK
        bitpos += 1

        instruction.BD8 = BD8Operand(instruction, bitpos, bitpos + 8)


class VleInstructionFormBC(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormBC, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:10])
        instruction.bits[0:10] = instruction.opcode

        # parse the following stuff
        bitpos = 10
        lean_format = spec[10:]

        self.bo32 = Bits('0b' + lean_format[:2])
        instruction.bits[10:12] = self.bo32

        self.bi32 = Bits('0b' + lean_format[2:6])
        instruction.bits[12:16] = self.bi32

        instruction.BD15 = BD15Operand(instruction, 16, 31)
        instruction.LK = 1 if lean_format[-1] == '1' else 0
        instruction.bits[31] = instruction.LK

class VleInstructionFormSeBC(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormSeBC, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        # parse the following stuff
        lean_format = spec[5:]

        self.bo16 = Bits('0b' + lean_format[:1])
        instruction.bits[5] = self.bo16

        self.bi16 = Bits('0b' + lean_format[1:3])
        instruction.bits[6:8] = self.bi16

        instruction.BD8 = BD8Operand(instruction, 8, 16)
        # this format does not have the LK option

class VleInstructionFormD(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormD, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        instruction.RD = RdOperand(instruction, 6, 11)
        instruction.RA = RdOperand(instruction, 11, 16)
        instruction.SI = D16Operand(instruction, 16, 32)

class VleInstructionFormD8(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormD8, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        instruction.RS = RdOperand(instruction, 6, 11)
        instruction.RA = RdOperand(instruction, 11, 16)
        instruction.D8 = D8Operand(instruction, 24, 32)
        instruction.bits[16:24] = Bits('0b' + spec[10:18])

class VleInstructionFormD16(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormD16, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        lean_format = spec[5:]
        instruction.RS = RxyaOperand(instruction, 6, 11)
        instruction.RA = RxyaOperand(instruction, 11, 16)
        instruction.D = D16Operand(instruction, 16, 32)

class VleInstructionFormI20(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormI20, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        instruction.RD = RdOperand(instruction, 6, 11)
        instruction.XO = SingleBitOperand(instruction, 16, 16)
        instruction.I20 = I20Operand(instruction, 11, 32)

class VleInstructionFormI16L(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormI16L, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        instruction.RD = RdOperand(instruction, 6, 11)
        instruction.bits[16:20] = Bits('0b' + spec[15:20])
        instruction.UI = UI16Operand(instruction, 11, 32)

class VleInstructionFormI16A(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormI16A, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        instruction.SI = SI16Operand(instruction, 6, 32)
        instruction.RA = RdOperand(instruction, 11, 16)
        instruction.bits[16:21] = Bits('0b' + spec[15:20])

class VleInstructionFormIM7(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormIM7, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:5])
        instruction.bits[0:6] = instruction.opcode

        instruction.UI = UI7Operand(instruction, 5, 12)
        instruction.RX = RxyaOperand(instruction, 12, 16)

class VleInstructionFormSD4(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormSD4, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:4])
        instruction.bits[0:6] = instruction.opcode

        instruction.SD4 = SD4Operand(instruction, 4, 8)
        instruction.RZ = RxyaOperand(instruction, 8, 12)
        instruction.RX = RxyaOperand(instruction, 12, 16)

class VleInstructionFormSD4_LS1(VleInstructionFormSD4):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormSD4_LS1, self).parse(instruction, spec)
        instruction.SD4 = SD4LS1Operand(instruction, 4, 8)

class VleInstructionFormSD4_LS2(VleInstructionFormSD4):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormSD4_LS2, self).parse(instruction, spec)
        instruction.SD4 = SD4LS2Operand(instruction, 4, 8)


class VleInstructionFormSCI8(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        # SCL: specifies a scale amount in SCI8-form Immediate instructions.
        # ..Scaling involves left shifting by 0, 8, 16, or 24 bits
        # F: Fill value used to fill the remaining 56 bits of a scaled-immediate 8 value.
        super(VleInstructionFormSCI8, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:5])
        instruction.bits[0:6] = instruction.opcode

        instruction.RS = RdOperand(instruction, 6, 11)
        instruction.RA = RdOperand(instruction, 11, 16)
        instruction.bits[16:20] = Bits('0b' + spec[10:14]) # CHECKME TODO
        instruction.RC = SingleBitOperand(instruction, 20, 21)
        instruction.F = SingleBitOperand(instruction, 21, 22)
        instruction.SCL = DualBitOperand(instruction, 22, 24)
        instruction.UI = UI8Operand(instruction, 24, 32)


class VleInstructionFormXFX(VleInstructionForm):
    # TODO: this form is specified in the EREF, move it to generic PPC
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormXFX, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        lean_format = spec[5:]
        instruction.RS = RdOperand(instruction, 6, 11)
        instruction.SPRN = SPRNOperand(instruction, 11, 21)
        instruction.bits[21:] = Bits('0b' + lean_format[-11:])

class VleInstructionFormXFX_CRM(VleInstructionForm):
    # TODO: this form is specified in the EREF, move it to generic PPC
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormXFX_CRM, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode

        instruction.RS = RdOperand(instruction, 6, 11)
        instruction.bits[11] = Bits('0b' + spec[8])
        instruction.CRM = CRMOperand(instruction, 12, 20)
        instruction.bits[20:] = Bits('0b' + spec[-12:])

class VleInstructionFormX(VleInstructionForm):
    # TODO: this form is specified in the EREF, move it to generic PPC
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormX, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:6])
        instruction.bits[0:6] = instruction.opcode
        instruction.E = SingleBitOperand(instruction, 16, 16)
        instruction.bits[21:31] = Bits('0b' + spec[13:-1])


class VleInstructionFormC(VleInstructionForm):
    def parse(self, instruction: Instruction, spec: str):
        super(VleInstructionFormC, self).parse(instruction, spec)
        # parse opcode
        instruction.opcode = Bits('0b' + spec[0:15])
        instruction.bits[0:15] = instruction.opcode
        instruction.L = SingleBitOperand(instruction, 15, 15)

class VleInstruction(Instruction):
    def __init__(self, form: VleInstructionForm, spec: str, addr: int = 0, bit_length=16, **kwargs):
        super(VleInstruction, self).__init__(spec, addr, bit_length)
        # VLE-specific attributes
        self.opcode = BitArray()

        # sanitize and parse VLE format, first
        self.spec = spec.upper().replace(' ', '')
        self.instruction_form = form
        self.instruction_form.parse(self, self.spec)

        # apply the operands using kwargs
        for k,v in kwargs.items():
            operand = getattr(self, k)
            # _get_register will translate a register to an integer _if_ v is a register.
            # in any other case, it will pass v as it is
            operand(operand._get_register(v))


    def _parse_fmt(self, fmt: str):
        # parse opcode
        self.opcode = BitArray('0b' + fmt[0:6])
        self.bits[0:6] = self.opcode

        # parse the following stuff
        bitpos = 6
        fmt_pos = 0
        lean_format = fmt.strip()
        lean_format = lean_format[6:]

        while True:
            c = lean_format[fmt_pos]
            if c == '0':
                self.bits[bitpos] = 0
                bitpos += 1
                fmt_pos += 1
            elif c == '1':
                self.bits[bitpos] = 1
                bitpos += 1
                fmt_pos += 1
            else:
                # check if at end or operand
                if len(lean_format[fmt_pos:]) >= 2:
                    # match operand
                    if match('R[XYA]', lean_format[fmt_pos:fmt_pos+2]):
                        # gp register, encoded with 4 bits in 16 bit instructions
                        if self.bit_length == 16:
                            setattr(self, lean_format[fmt_pos:fmt_pos+2], Operand(self, bitpos, bitpos + 4))
                            bitpos += 4
                            fmt_pos += 2
                        else: # 32 bit Rx encoding
                            setattr(self, lean_format[fmt_pos:fmt_pos + 2], Operand(self, bitpos, bitpos + 5))
                            bitpos += 5
                            fmt_pos += 2
                    elif match('SI', lean_format[fmt_pos:fmt_pos+2]):
                        # check if at end after SI
                        if len(lean_format[fmt_pos+2:]) < 1:
                            # if yes: that's it, make it extend to the end
                            self.SI = Operand(self, bitpos, self.bit_length)
                            break # done
                        else:
                            # check for slice
                            m = match('SI\[(\d{1,2}):(\d{1,2})\]', lean_format[fmt_pos:])
                            if m:
                                if not hasattr(self, 'SI'):
                                    self.SI = Operand(self, 0, 0)
                                # extract substring
                                self.SI.add_slice(bitpos, bitpos + int(m.group(2)) - int(m.group(1)) + 1)
                                # continue
                                bitpos += int(m.group(2)) - int(m.group(1))
                                fmt_pos += m.regs[0][1]
                            else:
                                raise Exception("error parsing SI")
                else:
                    # unknown case, error
                    raise Exception("Error parsing instruction!")

            if len(lean_format) <= fmt_pos:
                break # done





"""
ARITHMETIC
"""

# OIM5 form
class SeAddi(VleInstruction):
    def __init__(self, rX, oim5):
        # If se_cmpi, the contents of GPR(rX) are compared with the value of the zero-extended UI5 field,
        # treating the operands as signed integers. The result of the comparison is placed into CR field 0.
        super(SeAddi, self).__init__(form=VleInstructionFormOIM5(), spec='0 0 1 0 0 0 0 OIM5', RX=rX, OIM5=oim5)

class SeAdd(VleInstruction):
    def __init__(self, rX, rY):
        super(SeAdd, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 1 0   0 RY RX ', RY=rY, RX=rX)


class EAdd16i(VleInstruction):
    def __init__(self, rD, rA, SI):
        super(EAdd16i, self).__init__(form=VleInstructionFormD(), bit_length=32,
                                  spec='0 0 0 1 1 1 RD RA SI ', RD=rD, RA=rA, SI=SI)

class SeMullw(VleInstruction):
    def __init__(self, rX, rY):
        super(SeMullw, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 1 0 1 RY RX ', RY=rY, RX=rX)

class SeSub(VleInstruction):
    def __init__(self, rX, rY):
        super(SeSub, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 1 1 0 RY RX ', RY=rY, RX=rX)

# OIM5 form
class SeSubi(VleInstruction):
    def __init__(self, rX, oim5):
        # The sum of the contents of GPR(rX), the one’s complement of the zero-extended value of the offset OIM5
        # field (a final value in the range 1–32), and 1 is placed into GPR(rX).
        super(SeSubi, self).__init__(form=VleInstructionFormOIM5(), spec='0 0 1 0 0 1 Rc OIM5 1 1', RX=rX, OIM5=oim5)

class SeSubf(VleInstruction):
    def __init__(self, rX, rY):
        pass # not implemented

# I16A form
class EMull2i(VleInstruction):
    def __init__(self, rA, SI):
        super(EMull2i, self).__init__(form=VleInstructionFormI16A(), bit_length=32,
                                  spec='0 1 1 1 0 0 SI[0:4] RA 1 0 1 0 0 SI[5:15]', RA=rA, SI=SI)

class EAdd2i(VleInstruction):
    def __init__(self, rA, SI):
        super(EAdd2i, self).__init__(form=VleInstructionFormI16A(), bit_length=32,
                                      spec='0 1 1 1 0 0 SI[0:4] RA 1 0 0 0 1 SI[5:15]', RA=rA, SI=SI)


class EAdd2is(VleInstruction):
    def __init__(self, rA, SI):
        super(EAdd2is, self).__init__(form=VleInstructionFormI16A(), bit_length=32,
                                  spec='0 1 1 1 0 0 SI[0:4] RA 1 0 0 1 0 SI[5:15]', RA=rA, SI=SI)

"""
BITWISE
"""

# UI5 form
class SeAndi(VleInstruction):
    def __init__(self, rX, ui5):
        super(SeAndi, self).__init__(form=VleInstructionFormIM5(), spec='0 0 1 0 1 1 1 UI5 RX ', RX=rX, UI5=ui5)

class SeSlwi(VleInstruction):
    def __init__(self, rX, ui5):
        super(SeSlwi, self).__init__(form=VleInstructionFormIM5(), spec='0 1 1 0 1 1 0 UI5 RX ', RX=rX, UI5=ui5)

class SeSrwi(VleInstruction):
    def __init__(self, rX, ui5):
        super(SeSrwi, self).__init__(form=VleInstructionFormIM5(), spec='0 1 1 0 1 0 0 UI5 RX', RX=rX, UI5=ui5)


#class EAndi(VleInstruction):
    # e_andi -> Rc = 0
#    def __init__(self, rA, rS, UI):
#        super(EAndi, self).__init__(form=VleInstructionFormSCI8(), bit_length=32,
#                                    spec='0 0 0 1 1 0 RS RA 1 1 0 0 Rc F SCL UI8', RA=rA, RS=rS,
#                                    UI=(UI >> (SC * 8)), RC=1, SCL=SC)
#        raise Exception("Not implemented")

class EAndi_WithCR(VleInstruction):
    # e_andi. -> Rc = 1
    def __init__(self, rA, rS, UI):
        # check UI scaling
        SC = 0 # UI in range(0,0x100)
        if UI in range(0x100, 0x10000):
            if UI & 0x00FF != 0:
                raise Exception("EAndi_WithCR: incompatible immediate specified!")
            else:
                SC = 1
        if UI in range(0x10000, 0x1000000):
            if UI & 0x00FFFF != 0:
                raise Exception("EAndi_WithCR: incompatible immediate specified!")
            else:
                SC = 2
        if UI in range(0x1000000, 0xff000000):
            if UI & 0x00FFFFFF != 0:
                raise Exception("EAndi_WithCR: incompatible immediate specified!")
            else:
                SC = 3

        super(EAndi_WithCR, self).__init__(form=VleInstructionFormSCI8(), bit_length=32,
                                           spec='0 0 0 1 1 0 RS RA 1 1 0 0 Rc F SCL UI8', RA=rA, RS=rS,
                                           UI=(UI >> (SC * 8)), RC=1, SCL=SC)

class EAnd2i(VleInstruction):
    def __init__(self, rD, UI):
        super(EAnd2i, self).__init__(form=VleInstructionFormI16L(), bit_length=32,
                                    spec='0 1 1 1 0 0 RD UI[0:4] 1 1 0 0 1 UI[5:15]', RD=rD, UI=UI)


"""
MOVs
"""
class SeMr(VleInstruction):
    def __init__(self, rX, rY):
        super(SeMr, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 0 1 RY RX', RY=rY, RX=rX)

class SeMtar(VleInstruction):
    def __init__(self, arX, rY):
        super(SeMtar, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 1 0 RY ARX', RY=rY, ARX=arX)

class SeMfar(VleInstruction):
    def __init__(self, rX, arY):
        super(SeMfar, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 1 1 ARY RX', ARY=arY, RX=rX)

class Mtspr(VleInstruction):
    def __init__(self, spr, rS):
        super(Mtspr, self).__init__(form=VleInstructionFormXFX(), bit_length=32,
                                    spec='0 1 1 1 1 1 rS SPRN[5–9] SPRN[ 0–4] 0 1 1 1 0 1 0 0 1 1 0 ', SPRN=spr, RS=rS)

class Mfspr(VleInstruction):
    def __init__(self, rD, spr):
        super(Mfspr, self).__init__(form=VleInstructionFormXFX(), bit_length=32,
                                    spec='0 1 1 1 1 1 rD sprn 5:9 sprn0:4 0 1 0 1 0 1 0 0 1 1 0', SPRN=spr, RS=rD)

class Mtcrf(VleInstruction):
    def __init__(self, CRM, rS):
        super(Mtcrf, self).__init__(form=VleInstructionFormXFX_CRM(), bit_length=32,
                                    spec='0 1 1 1 1 1 rS 0 CRM 0 0 0 1 0 0 1 0 0 0 0 0', CRM=CRM, RS=rS)

class Mfcr(VleInstruction):
    def __init__(self, rD):
        super(Mfcr, self).__init__(form=VleInstructionFormXFX(), bit_length=32,
                                    spec='0 1 1 1 1 1 rD 0 0 0 0 0 0 0 0 0 1 0 0 1 1 0', SPRN=0, RS=rD)


class SeMtctr(VleInstruction):
    def __init__(self, rX):
        super(SeMtctr, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 0 0 1 0 1 1 RX', RX=rX)

class SeMfctr(VleInstruction):
    def __init__(self, rX):
        super(SeMfctr, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 0 0 1 0 1 0 RX ', RX=rX)

class SeMtlr(VleInstruction):
    def __init__(self, rX):
        super(SeMtlr, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 0 0 1 0 0 1 RX', RX=rX)

class SeMflr(VleInstruction):
    def __init__(self, rX):
        super(SeMflr, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 0 0 0 0 1 0 0 0 RX', RX=rX)



class Wrteei(VleInstruction):
    # Write MSR External Enable Immediate
    def __init__(self, E):
        super(Wrteei, self).__init__(form=VleInstructionFormX(), bit_length=32,
                                     spec='0 1 1 1 1 1 /// E /// 0 0 1 0 1 0 0 0 1 1 /', E=E)



"""
CONTROL FLOW / COMPARE
"""

# RR form
class SeCmp(VleInstruction):
    def __init__(self, rX, rY):
        super(SeCmp, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 1 1 0 0 RY RX ', RY=rY, RX=rX)

class SeCmpl(VleInstruction):
    def __init__(self, rX, rY):
        super(SeCmpl, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 1 1 0 1 RY RX', RY=rY, RX=rX)

class SeCmph(VleInstruction):
    def __init__(self, rX, rY):
        super(SeCmph, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 1 1 1 0 RY RX', RY=rY, RX=rX)

class SeCmphl(VleInstruction):
    def __init__(self, rX, rY):
        super(SeCmphl, self).__init__(form=VleInstructionFormRR(), spec='0 0 0 0 1 1 1 1 RY RX ', RY=rY, RX=rX)

# OIM5 form
class SeCmpli(VleInstruction):
    def __init__(self, rX, oim5):
        super(SeCmpli, self).__init__(form=VleInstructionFormOIM5(), spec='0 0 1 0 0 0 1 OIM5', RX=rX,
                                     OIM5=oim5)
        
# OIM5 form
class SeCmpi(VleInstruction):
    def __init__(self, rX, oim5):
        # If se_cmpi, the contents of GPR(rX) are compared with the value of the zero-extended UI5 field,
        # treating the operands as signed integers. The result of the comparison is placed into CR field 0.
        super(SeCmpi, self).__init__(form=VleInstructionFormOIM5(), spec='0 0 1 0 1 0 1 UI5 RX', RX=rX, OIM5=oim5+1)


class EB(VleInstruction):
    def __init__(self, bd24):
        super(EB, self).__init__(form=VleInstructionFormBD24(), bit_length=32, spec='0 1 1 1 1 0 0 BD24 0', BD24=bd24)

class EBl(VleInstruction):
    def __init__(self, bd24):
        super(EBl, self).__init__(form=VleInstructionFormBD24(),  bit_length=32, spec='0 1 1 1 1 0 0 BD24 1', BD24=bd24)


class EBc(VleInstruction):
    def __init__(self, bd15):
        # bi32 = 0
        # bo32 = 10
        super(EBc, self).__init__(form=VleInstructionFormBC(), bit_length=32, spec='0 1 1 1 1 0 1   0   0   0 10 0 BD15 0')

class EBne(VleInstruction):
    def __init__(self, bd15):
        # bi32 = 0010 = 2 = CR34 (cr offset)
        # bo32 = 00 (equal bit must be false)
        # 0 1 1 1 1 0 1   0   0   0 BO32 BI32 BD15 LK
        super(EBne, self).__init__(form=VleInstructionFormBC(), bit_length=32, spec='0 1 1 1 1 0 1   0   0   0 00 0010 BD15 0', BD15=bd15)

class EBe(VleInstruction):
    def __init__(self, bd15):
        # bi32 = 0010 = 2 = CR34 (cr offset, eq bit)
        # bo32 = 01 (equal bit must be true)
        # 0 1 1 1 1 0 1   0   0   0 BO32 BI32 BD15 LK
        super(EBe, self).__init__(form=VleInstructionFormBC(), bit_length=32, spec='0 1 1 1 1 0 1   0   0   0 01 0010 BD15 0', BD15=bd15)

class EBgt(VleInstruction):
    def __init__(self, bd15):
        # bi32 = 0001 = 1 = CR33 (cr offset, gt bit)
        # bo32 = 01 (gt bit must be true)
        # 0 1 1 1 1 0 1   0   0   0 BO32 BI32 BD15 LK
        super(EBgt, self).__init__(form=VleInstructionFormBC(), bit_length=32, spec='0 1 1 1 1 0 1   0   0   0 01 0001 BD15 0', BD15=bd15)


class EBlt(VleInstruction):
    def __init__(self, bd15):
        # bi32 = 0000 = 0 = CR32 (cr offset, lt bit)
        # bo32 = 01 (lt bit must be true)
        # 0 1 1 1 1 0 1   0   0   0 BO32 BI32 BD15 LK
        super(EBlt, self).__init__(form=VleInstructionFormBC(), bit_length=32, spec='0 1 1 1 1 0 1   0   0   0 01 0000 BD15 0', BD15=bd15)


class SeB(VleInstruction):
    def __init__(self, bd8):
        super(SeB, self).__init__(form=VleInstructionFormBD8(), spec='1 1 1 0 1 0 0 0 BD8 ', BD8=bd8)

class SeBl(VleInstruction):
    def __init__(self, bd8):
        super(SeBl, self).__init__(form=VleInstructionFormBD8(), spec='1 1 1 0 1 0 0 1 BD8 ', BD8=bd8)


class SeBeq(VleInstruction):
    def __init__(self, bd8):
        # bi16 = 10 = 2 = CR34 (cr offset, eq bit)
        # bo16 = 1 (eq bit must be true)
        # 1 1 1 0 0 BO16 BI16 BD8
        super(SeBeq, self).__init__(form=VleInstructionFormSeBC(),  bit_length=16, spec='1 1 1 0 0 1 10 BD8', BD8=bd8)

class SeBne(VleInstruction):
    def __init__(self, bd8):
        # bi16 = 10 = 2 = CR34 (cr offset, eq bit)
        # bo16 = 0 (eq bit must be false)
        # 1 1 1 0 0 BO16 BI16 BD8
        super(SeBne, self).__init__(form=VleInstructionFormSeBC(),  bit_length=16, spec='1 1 1 0 0 0 10 BD8', BD8=bd8)

class SeBlt(VleInstruction):
    def __init__(self, bd8):
        # bi16 = 00 = 0 = CR32 (cr offset, lt bit)
        # bo16 = 1 (lt bit must be true)
        # 1 1 1 0 0 BO16 BI16 BD8
        super(SeBlt, self).__init__(form=VleInstructionFormSeBC(),  bit_length=16, spec='1 1 1 0 0 1 00 BD8', BD8=bd8)

class SeBgt(VleInstruction):
    def __init__(self, bd8):
        # bi16 = 01 = 1 = CR33 (cr offset, gt bit)
        # bo16 = 1 (gt bit must be true)
        # 1 1 1 0 0 BO16 BI16 BD8
        super(SeBgt, self).__init__(form=VleInstructionFormSeBC(),  bit_length=16, spec='1 1 1 0 0 1 01 BD8', BD8=bd8)

# Link/Ctr Register related

class SeBlr(VleInstruction):
    def __init__(self):
        super(SeBlr, self).__init__(form=VleInstructionFormC(),  bit_length=16,
                                    spec='0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 LK', L=0)

class SeBlrl(VleInstruction):
    def __init__(self):
        super(SeBlrl, self).__init__(form=VleInstructionFormC(),  bit_length=16,
                                    spec='0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 LK', L=1)

class SeBctr(VleInstruction):
    def __init__(self):
        super(SeBctr, self).__init__(form=VleInstructionFormC(),  bit_length=16,
                                    spec='0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 LK', L=0)

class SeBctrl(VleInstruction):
    def __init__(self):
        super(SeBctrl, self).__init__(form=VleInstructionFormC(),  bit_length=16,
                                    spec='0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 LK', L=1)

"""
LOAD / STORE OPS
"""
class EStw(VleInstruction):
    def __init__(self, rS, rA, D):
        super(EStw, self).__init__(form=VleInstructionFormD16(), bit_length=32, spec='0 1 0 1 0 1 RS RA D', RS=rS, RA=rA, D=D)

class SeSth(VleInstruction):
    def __init__(self, rZ, rX, sd4):
        super(SeSth, self).__init__(form=VleInstructionFormSD4_LS1(), spec='1 0 1 1 SD4 RZ RX', RX=rX, RZ=rZ, SD4=sd4)

class SeStw(VleInstruction):
    def __init__(self, rZ, rX, sd4):
        super(SeStw, self).__init__(form=VleInstructionFormSD4_LS2(), spec='1 1 0 1 SD4 RZ RX', RX=rX, RZ=rZ, SD4=sd4)

class SeStb(VleInstruction):
    def __init__(self, rZ, rX, sd4):
        super(SeStb, self).__init__(form=VleInstructionFormSD4(), spec='1 0 0 1 SD4 RZ RX', RX=rX, RZ=rZ, SD4=sd4)

class EStmw(VleInstruction):
    def __init__(self, rS, rA, D):
        super(EStmw, self).__init__(form=VleInstructionFormD8(), bit_length=32,
                                   spec='0 0 0 1 1 0 RS RA 0 0 0 0 1 0 0 1 D8 ', RS=rS, RA=rA, D8=D)

class ELi(VleInstruction):
    def __init__(self, rD, I20):
        super(ELi, self).__init__(form=VleInstructionFormI20(), bit_length=32,
                                  spec='0 1 1 1 0 0 RD LI20[4-8] 0 LI20[0-3] LI20[9-19]', RD=rD, I20=I20, XO=0)

class ELis(VleInstruction):
    def __init__(self, rD, UI):
        super(ELis, self).__init__(form=VleInstructionFormI16L(), bit_length=32,
                                  spec='0 1 1 1 0 0 RD UI[0-4] 1 1 1 0 0 UI[5-15]', RD=rD, UI=UI)

class ELmw(VleInstruction):
    def __init__(self, rD, rA, D):
        super(ELmw, self).__init__(form=VleInstructionFormD8(), bit_length=32,
                                   spec='0 0 0 1 1 0 RD RA 0 0 0 0 1 0 0 0 D8', RS=rD, RA=rA, D8=D)

class SeLi(VleInstruction):
    def __init__(self, rX, UI):
        super(SeLi, self).__init__(form=VleInstructionFormIM7(), spec='0 1 0 0 1 UI7 RX', RX=rX, UI=UI)

class SeLwz(VleInstruction):
    def __init__(self, rZ, rX, sd4):
        super(SeLwz, self).__init__(form=VleInstructionFormSD4_LS2(), spec='1 1 0 0 SD4 RZ RX', RX=rX, RZ=rZ, SD4=sd4)

class SeLhz(VleInstruction):
    def __init__(self, rZ, rX, sd4):
        super(SeLhz, self).__init__(form=VleInstructionFormSD4_LS1(), spec='1 0 1 0 SD4 RZ RX', RX=rX, RZ=rZ, SD4=sd4)

class SeLbz(VleInstruction):
    def __init__(self, rZ, rX, sd4):
        super(SeLbz, self).__init__(form=VleInstructionFormSD4(), spec='1 0 0 0 SD4 RZ RX', RX=rX, RZ=rZ, SD4=sd4)