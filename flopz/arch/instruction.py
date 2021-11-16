from flopz.arch.register import Register
from flopz.core.addressable_object import AddressableObject
from bitstring import BitArray
import operator


class Instruction(AddressableObject):
    def __init__(self, fmt: str, addr: int = 0, bit_length: int = 32):
        """
        fmt: specific instruction format, as string
        addr: when instantiating, the address at which this instruction lives
        """
        super(Instruction, self).__init__(object_addr=addr)
        self.format = fmt
        self.bit_length = bit_length
        self.bits = BitArray(length=self.bit_length)
        self.opcode_mask = None

    def bytes(self) -> bytes:
        """
        :returns: the encoded instruction as bytes
        """
        swapped_bits = self.bits.copy()
        return swapped_bits.bytes

    def size_bits(self) -> int:
        return len(self.bits)

    def size_bytes(self) -> int:
        return len(self.bits.bytes)


class ArbitraryBytesInstruction(Instruction):
    def __init__(self, bytes: bytes):
        self._bytes = bytes
        self.bit_length = len(bytes) * 8
        self.bits = BitArray(self._bytes)

    def bytes(self) -> bytes:
        return self._bytes


