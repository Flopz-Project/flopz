from flopz.arch.exceptions import *
from flopz.arch.register import Register
from flopz.arch.instruction import Instruction
from bitstring import BitArray
from typing import Iterable, Any


class Operand:
    """Class for instruction parameter setting and accessing.

    Operands are added to instruction classes to define how instructions encode certain parameters in their
    bit representation. They hold a reference to their assigned instruction and the bitpositions where they can
    access and set their value from/to the BitArray underlying the instruction.
    Bitpositions are inclusive for start, exclusive for end (like slicing etc.).

    Parameters:
        instruction: The instruction the operand is assigned to.
        bitpos_start: The first bit of the instruction belonging to the operand.
        bitpos_end: The first bit after the bits assigned to the operands (end of slice / exclusive).
    """
    def __init__(self, instruction: Instruction, bitpos_start: int, bitpos_end: int):
        self.instruction = instruction
        self.bitpos_start = bitpos_start
        self.bitpos_end = bitpos_end

    def __call__(self, *args, **kwargs):
        if len(args) < 1:
            # get!
            return self.instruction.bits[self.bitpos_start:self.bitpos_end]
        else:
            # set!
            self.instruction.bits[self.bitpos_start:self.bitpos_end] = args[0]

    @staticmethod
    def _get_register(reg):
        """
        If the argument is a Register class, return the value that register is representing.
        """
        # helper method to access register values as int or using Register class
        if isinstance(reg, Register):
            return reg.value()
        else:
            return reg


class BitsOperand(Operand):
    """
     Class for instruction parameter setting and accessing.

     Extends the basic Operand class with more capabilities and better error handling.
     The intended amount of bits assigned to the operand can be given to reduce implementation errors.
     Additionally it can be specified if the value to be encoded or read is shifted or if it is signed.

     Attributes:
         instruction: The instruction the operand is assigned to.
         bitpos_start: The first bit of the instruction belonging to the operand.
         bitpos_end: The first bit after the bits assigned to the operands (end of slice / exclusive).
         bits: Amount of bits assigned to the operand.
         signed: Is the value to be encoded signed.
         shift: Is the encoded value shifted (right shift).
     """
    def __init__(self, instruction: Instruction, bitpos_start: int, bitpos_end: int, bits: int = None,
                 signed: bool = False, shift: int = 0):
        if bits is not None and bitpos_end - bitpos_start != bits:
            raise Exception("Invalid parameters for BitOperand")
        else:
            bits = bitpos_end - bitpos_start
        super().__init__(instruction, bitpos_start, bitpos_end)
        self.bits = bits
        self.signed = signed
        self.shift = shift

    def __call__(self, *args):
        """
        Encodes the value given or returns the encoded value when not given an argument.
        """
        if len(args) < 1:
            # get
            return super().__call__() << self.shift
        else:
            # set
            arg = self._get_register(args[0]) >> self.shift
            if not self.signed:
                if arg in range(2**self.bits):
                    self.instruction.bits[self.bitpos_start: self.bitpos_end] = arg
                else:
                    raise ValueError(f"Bit operand: value {arg} out of range [0 - {(2**self.bits)-1}]"
                                     f" (shift {self.shift})")
            else:
                if arg in range(-(2 ** (self.bits - 1)), (2 ** (self.bits - 1))):
                    self.instruction.bits[self.bitpos_start: self.bitpos_end] = arg
                else:
                    raise ValueError(
                        f"Bit operand: value {arg} out of range [{-(2 ** (self.bits - 1))}"
                        f" - {(2 ** (self.bits - 1)) - 1}] (shift {self.shift})")


# used for operands whose information is encoded in multiple slices in the instruction
class CombinedOperand(Operand):
    """
    Used to combine multiple operand to represent a single value.

    Many instructions have values encoded in multiple bitslices and bitpositions.
    A normal operand can only represent a continuous slice of bits, so this class is used to combine multiple
    operands to be able to represent more complex structures.

    Parameters:
        *args: The operands that need to be combined. Ordered most significant operand first.
        signed: Is the encoded value signed.
        shift: Is the encoded value shifted.
    """
    def __init__(self, *args: Iterable[Any], signed: bool = False, shift=0):
        if len(args) < 2:
            raise Exception("CombinedOperand needs at least 2 Operands")
        if not all(map(lambda arg: isinstance(arg, Operand), args)):
            raise Exception("CombinedOperand can only accept args of type Operand")
        self.operands = args
        if not all(map(lambda op: op.instruction == self.operands[0].instruction, self.operands[1:])):
            raise Exception("CombinedOperand can only work with operands of the same instruction")
        if any(map(lambda op: op.signed, self.operands)):
            raise Exception("CombinedOperand can only combine unsigned operands")
        if any(map(lambda op: op.shift != 0, self.operands)):
            raise Exception("CombinedOperand can only combine unshifted operands")

        super().__init__(self.operands[0].instruction, bitpos_start=self.operands[0].bitpos_start, bitpos_end=self.operands[-1].bitpos_end)

        self.bit_length = sum(op.bits for op in self.operands)
        self.signed = signed
        self.shift=shift

    def __call__(self, *args, **kwargs):
        """
        Encodes the value given or returns the encoded value when not given an argument.
        """
        if len(args) < 1:
            # combine value from sub-operands
            res = self.operands[0]()
            for x in (op() for op in self.operands[1:]):
                res.append(x)
            return res << self.shift
        else:
            # set values in sub-operands
            arg = self._get_register(args[0]) >> self.shift
            if not self.signed:
                power = 2 ** self.bit_length
                arg = arg
                if arg in range(power):
                    full = BitArray(length=self.bit_length, uint=arg)
                    self.set_suboperands(full)
                else:
                    raise ValueError(f"Invalid value {arg} for {self.bit_length}-bit operand")
            else:
                power = 2 ** (self.bit_length - 1)
                arg = arg
                if arg in range(-power, power-1):
                    full = BitArray(length=self.bit_length, int=arg)
                    self.set_suboperands(full)

                else:
                    raise ValueError(f"Invalid value {arg} for {self.bit_length}-bit signed operand")

    def set_suboperands(self, full):
        """
        Sets the suboperands from msb to lsb.
        """
        offset = 0
        for op in self.operands:
            op(full[offset: offset+op.bits].uint)
            offset += op.bits