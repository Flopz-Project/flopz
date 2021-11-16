from typing import List
from flopz.arch.instruction import Instruction


class AutoInstruction(Instruction):
    """
    An AutoInstruction is a mini-module that expands into one or more architecture-specific instructions
    Each Auto*Type has to be implemented for each architecture individually
    For VLE, for example, AutoJmp could expand into se_b for short jumps or e_b for longer jumps
    Subclasses need to override expand() and (optionally) size_bytes() and length()
    """
    def __init__(self, addr: int = 0):
        super(AutoInstruction, self).__init__(fmt='', addr=addr)

    def size_bits(self) -> int:
        return self.size_bytes() * 8

    def size_bytes(self) -> int:
        return sum([ins.size_bytes() for ins in self.expand()])

    def expand(self) -> List[Instruction]:
        """
        :returns: Regular instructions.
        """
        return [self]  # override this

    def bytes(self) -> bytes:
        """
        :returns: this instruction, expanded and assembled to bytes
        """
        instructions = self.expand()
        return b''.join([ins.bytes() for ins in instructions])

