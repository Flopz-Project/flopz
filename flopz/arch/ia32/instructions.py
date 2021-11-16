from bitstring import BitArray

from flopz.arch.instruction import Instruction
from flopz.arch.ia32.registers import IA32_Register
from flopz.arch.ia32.ia32_generic_arch import ProcessorMode




"""
Prefixes and Fields that make up IA-32 instructions
"""


# REX
class REX:
    def __init__(self, w=0, r=0, x=0, b=0):
        if not all([0<=v<=1 for v in [w, r, x, b]]):
            raise Exception("Invalid bit for REX byte")
        self.w = w
        self.r = r
        self.x = x
        self.b = b

    def encode(self):
        return BitArray(bin='0100') + BitArray(length=4, uint=8*self.w+4*self.r+2*self.x+self.b)


# Opcode


class IA32Opcode:
    def __init__(self, opcode: int, opc_encoding: int = None, mandatory: BitArray = None, op_size: int = 64,
                 mode: ProcessorMode = ProcessorMode.LONG, force_rex=False):
        # TODO check validity of all values
        self.base_opcode = opcode
        self.effective_opcode = self.base_opcode
        self.prefix = None
        self.mandatory_prefix = mandatory

        # is a register encoded with the opcode
        self.opcode_register_encoding = False
        if opc_encoding is not None:
            self.opcode_register_encoding = True

        if force_rex:
            self.rex = REX()
        else:
            self.rex = None

        # check for operand size encoding
        if mode == ProcessorMode.LONG:
            if op_size == 64:
                self.set_rex_bit('w')
            elif op_size == 16:
                self.prefix = BitArray('0x66')
        elif mode == ProcessorMode.PROTECTED:
            if op_size == 32:
                self.prefix = BitArray('0x66')

        # check for in operand encoding
        if self.opcode_register_encoding:
            # set opcode 3lsb and (in 64-bit mode) rex.b
            self.effective_opcode += opc_encoding % 8
            self.set_rex_bit('b')if opc_encoding >= 8 else 0

    def encode(self):
        # result is prefix (optional) + mand_prefix (optional) + rex + effective_opcode
        encoding = BitArray(length=8, uint=self.effective_opcode)
        if self.rex is not None:
            encoding.prepend(self.rex.encode())
        if self.mandatory_prefix is not None:
            encoding.prepend(self.mandatory_prefix)
        if self.prefix is not None:
            encoding.prepend(self.prefix)
        return encoding

    def get_encoded(self):
        if self.opcode_register_encoding:
            return self.rex.b * 8 + self.effective_opcode - self.base_opcode
        else:
            return None

    def set_rex_bit(self, bit: str, val=1):
        if bit not in ['w', 'r', 'x', 'b']:
            raise Exception('Invalid REX bit')

        if self.rex is None:
            self.rex = REX()

        if bit == 'w':
            self.rex.w = val
        if bit == 'r':
            self.rex.r = val
        if bit == 'x':
            self.rex.x = val
        if bit == 'b':
            self.rex.b = val


# ModR/M
class ModRM:
    def __init__(self, mod=3, reg=0, rm=0):
        self.mod = mod
        self.reg = reg
        self.rm = rm

    def encode(self):
        return BitArray(length=2, uint=self.mod) + BitArray(length=3, uint=self.reg) + BitArray(length=3, uint=self.rm)


# SID


# Displacement


# Immediate
class Immediate:
    def __init__(self, value: int, byte_size):
        self.value = value
        self.byte_size = byte_size

    def encode(self):
        # immediate values are encoded little endian
        swapped_bytes = BitArray(length=self.byte_size*8, uint=self.value)
        swapped_bytes.byteswap()
        return swapped_bytes



class IA32InstructionForm:
    def parse(self, instruction: Instruction):
        pass


class IA32ModrmForm(IA32InstructionForm):
    def parse(self, instruction: Instruction):
        instruction.reg = lambda: instruction.modrm.reg
        instruction.rm = lambda: instruction.modrm.rm

class IA32EncodedForm(IA32InstructionForm):
    def parse(self, instruction: Instruction):
        instruction.reg = lambda: instruction.opcode.get_encoded()
        instruction.imm = lambda: instruction.immediate.value


"""
Instructions
"""


class IA32Instruction(Instruction):
    def __init__(self, form: IA32InstructionForm, opcode: IA32Opcode, modrm=None, sib=None, displacement=None, immediate=None, addr = 0):

        self.opcode = opcode
        self.modrm = modrm
        self.sib = sib
        self.displacement = displacement
        self.immediate=immediate
        self.instruction_form = form
        self.instruction_form.parse(self)

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


class Mov(IA32Instruction):
    def __init__(self, dst, src):
        if not isinstance(dst, IA32_Register):
            raise Exception("MOV destination is no valid register")
        opsize = dst.bit_size
        if isinstance(src, IA32_Register):
            # move register content to register
            if src.bit_size != opsize:
                raise Exception("Invalid operand size for target register")

            # TODO relative addressing
            form = IA32ModrmForm()
            if opsize == 8:
                if dst.requires_rex() or src.requires_rex():
                    if dst.is_high() or src.is_high():
                        raise Exception("Invalid to encode this register combination")
                    # force rex byte to encode those registers
                    oc = IA32Opcode(0x88, op_size=opsize, force_rex=True)
                else:
                    oc = IA32Opcode(0x88, op_size=opsize)
            else:
                oc = IA32Opcode(0x89, op_size=opsize)
            modrm = ModRM(reg=src.get_val(), rm=dst.get_val())
            super().__init__(form, oc, modrm=modrm)
        else:
            # move immediate to register
            form = IA32EncodedForm()
            if opsize == 8:
                oc = IA32Opcode(0xB0, opc_encoding=dst.get_val(), op_size=opsize, force_rex=dst.requires_rex())
            else:
                oc = IA32Opcode(0xB8, opc_encoding=dst.get_val(), op_size=opsize)
            imm = Immediate(src, byte_size=opsize//8)
            super().__init__(form, oc, immediate=imm)


class Add(IA32Instruction):
    def __init__(self, dst, src):
        if not isinstance(dst, IA32_Register):
            raise Exception("ADD destination is no valid register")
        opsize = dst.bit_size

        if isinstance(src, IA32_Register):
            # add register to register
            if src.bit_size != opsize:
                raise Exception("Invalid operand size for target register")

            # TODO relative addressing

            form = IA32ModrmForm()
            if opsize == 8:
                if dst.requires_rex() or src.requires_rex():
                    if dst.is_high() or src.is_high():
                        raise Exception("Invalid to encode this register combination")
                    # force rex byte to encode those registers
                    oc = IA32Opcode(0x02, op_size=opsize, force_rex=True)
                else:
                    oc = IA32Opcode(0x02, op_size=opsize)
            else:
                oc = IA32Opcode(0x03, op_size=opsize)
            modrm = ModRM(reg=dst.get_val(), rm=src.get_val())
            super().__init__(form, oc, modrm=modrm)
        else:
            # add immediate to register
            form = IA32ModrmForm()
            if opsize == 8:
                oc = IA32Opcode(0x80, op_size=opsize, force_rex=dst.requires_rex())
            else:
                oc = IA32Opcode(0x81, op_size=opsize)
            modrm = ModRM(reg=0, rm=dst.get_val())
            imm = Immediate(src, byte_size=opsize//8)
            super().__init__(form, oc, modrm=modrm, immediate=imm)

# TODO relative addressing

# TODO rooting out invalid register combinations more effectively (ah, r15l or sth like that is not possible to encode)