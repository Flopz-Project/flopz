from bitstring import BitArray

from flopz.arch.ia32.modes import ProcessorMode
from math import log2

"""
Prefixes and Fields / Bytes that make up IA-32 instructions
"""


# REX
class REX:
    """
    The REX byte that optionally precedes the opcode byte.

    The REX byte holds flag to extend the operand size of the instruction (w)
    and the values of the encoded registers (r register, x index, b base).
    Additionally the presence of the REX byte also switches from addressing the upper half of the first 4 registers to
    addressing spl-dil.
    """
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
    """
    The opcode byte and optional prefixes and optional REX byte.

    This class holds the effective opcode of the instruction. Sometimes instructions encode additional
    information in the 3 lsb of the opcode, which can be added as opc_encoding.
    Additionally, some instructions require a mandatory prefix or the instructions operand size requires
    prefixes that change the effective operand size, which this class will handle and encode correctly.
    Also handles access to the REX byte of the instruction. Therefore the opcode object can be given to
    ModRM or SIB inits so they can set required bits.
    """
    def __init__(self, opcode: int, opc_encoding: int = None, mandatory: BitArray = None, op_size: int = 64,
                 mode: ProcessorMode = ProcessorMode.LONG, force_rex=False):
        """
        Sets the base opcode and encodes optional opcode encoding. Determines necessary prefixes for operand size.

        Parameters:
            opcode (int): the base opcode of the instruction.
            opcode_encoding (int): Optional additional register info encoded in the opcode byte.
            mandatory (BitArray): Optional mandatory prefix of the instruction.
            op_size (int): Operand size of the instruction.
            mode (ProcessorMode): Mode the processor is running on.
            force_rex(bool): Is a REX required even if no REX flags are set.
        """
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
            if opc_encoding >= 8 and mode == ProcessorMode.LONG:
                self.set_rex_bit('b')

    def encode(self):
        """
        Returns the BitArray that holding the opcode information
        can be combined with the other encodings to form the full instruction.
        """
        # result is prefix (optional) + mand_prefix (optional) + rex + effective_opcode
        if self.effective_opcode <= 0xFF:
            encoding = BitArray(length=8, uint=self.effective_opcode)
        else:
            encoding = BitArray(length=16, uint=self.effective_opcode)
        if self.rex is not None:
            encoding.prepend(self.rex.encode())
        if self.mandatory_prefix is not None:
            encoding.prepend(self.mandatory_prefix)
        if self.prefix is not None:
            encoding.prepend(self.prefix)
        return encoding

    def get_encoded(self):
        """
        Get the additional information encoded in the opcode.
        """
        if self.opcode_register_encoding:
            return self.rex.b * 8 + self.effective_opcode - self.base_opcode
        else:
            return None

    def set_rex_bit(self, bit: str, val=1):
        """
        Set or unset REX bits/flags.
        """
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

class ExtendableBitfieldDescriptor:
    """
    Descriptor to handle access to the different fields of the ModRM or SIB byte.

    As the fields can not be set or read without considering the flags in the REX bits, this descriptor
    will consider its given REX flag (r, x or b) when returning its value and will set the necessary flags
    in the flaglist when setting the value. Flags from the flaglist will then be applied by calls to
    ModRM or SIB's set_needed_rexflags().
    """
    def __init__(self, flag: str):
        self.flag = flag
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance: 'ModRM', owner=None):
        if instance is None:
            return self
        if self._name is not None:
            field_val = getattr(instance, f"_{self._name}")
            if self.flag in instance.flaglist:
                field_val += 8
            return field_val
        else:
            return None

    def __set__(self, instance: 'ModRM', value):
        if instance is None:
            return self
        if self._name is not None:
            if value >= 8 and self.flag not in instance.flaglist:
                instance.flaglist.append(self.flag)
                value -= 8
            elif value < 8 and self.flag in instance.flaglist:
                instance.flaglist.remove(self.flag)
            setattr(instance, f"_{self._name}", value)
            instance.set_needed_rexflags()


class ModRM:
    """
    Represents the ModRM byte of an IA32 instruction.

    This byte includes the reg and rm fields and the 2 bit mode.
    The reg and rm fields hold the registers used for addressing (when no SIB is used).
    The mode is used to determine the addressing mode (3 for register-direct addressing, 0-2 for indirect addressing
    with different displacements).
    A rm of 4 with indirect addressing indicates a SIB byte is used to encode the addressing.
    """

    reg = ExtendableBitfieldDescriptor('r')
    rm = ExtendableBitfieldDescriptor('b')

    def __init__(self, mod: int = 3, reg: int = 0, rm: int = 0, opcode: IA32Opcode = None):
        self.flaglist = list()
        self.opcode = opcode
        self._reg = None
        self._rm = None
        self.mod = mod
        self.reg = reg
        self.rm = rm

        self.set_needed_rexflags()

    def set_opcode(self, opcode: IA32Opcode):
        self.opcode = opcode

    def set_needed_rexflags(self):
        if self.opcode is not None:
            for flag in self.flaglist:
                self.opcode.set_rex_bit(flag)

    def encode(self):
        return BitArray(length=2, uint=self.mod) + BitArray(length=3, uint=self._reg) + BitArray(length=3, uint=self._rm)


# SIB
class SIB:
    """
    Represents the SIB byte of an IA32 instruction.

    This byte includes the 2 bit scale field and the base and index registers used for addressing.
    The base field holds the register that holds the base address, while the index field holds the index register.
    The actual scale is encoded as log2(scale), so the scale can be 1, 2, 4 or 8.
    If a displacement is present is dependant on the ModRM mod field.
    If the index is the stack pointer register this means no index is used.
    If the base is the base pointer register in mod 0, this means no base is used.
    """

    index = ExtendableBitfieldDescriptor('x')
    base = ExtendableBitfieldDescriptor('b')

    def __init__(self, scale: int = 0, index: int = 0, base: int = 0, opcode: IA32Opcode = None):
        self.flaglist = list()
        self.opcode = opcode
        self.scale = scale
        self._index = None
        self._base = None
        self.index = index
        self.base = base

        self.set_needed_rexflags()

    def set_opcode(self, opcode: IA32Opcode):
        self.opcode = opcode

    def set_needed_rexflags(self):
        if self.opcode is not None:
            for flag in self.flaglist:
                self.opcode.set_rex_bit(flag)

    def encode(self):
        return BitArray(length=2, uint=int(log2(self.scale))) + BitArray(length=3, uint=self._index) + \
               BitArray(length=3, uint=self._base)


# Displacement
class Displacement:
    """
    Represents the Displacement of an IA32 instruction.
    """
    def __init__(self, displacement: int, byte_size: int):
        self.displacement = displacement
        self.byte_size = byte_size

    def encode(self):
        # displacement values are encoded little endian
        swapped_bytes = BitArray(length=self.byte_size*8, int=self.displacement)
        swapped_bytes.byteswap()
        return swapped_bytes


# Immediate
class Immediate:
    """
    Represents the Immediate value of an IA32 instruction.
    """
    def __init__(self, value: int, byte_size: int):
        self.value = value
        self.byte_size = byte_size

    def encode(self):
        # immediate values are encoded little endian
        swapped_bytes = BitArray(length=self.byte_size*8, int=self.value)
        swapped_bytes.byteswap()
        return swapped_bytes
