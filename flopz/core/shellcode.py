from flopz.core.addressable_object import AddressableObject
from flopz.core.assembler import Assembler


class Shellcode(AddressableObject):
    """
    A Shellcode is an AddressableObject that contains a bunch of instructions that can be assembled
    """
    def __init__(self, instructions: list = [], address: int = 0):
        super(Shellcode, self).__init__(object_addr=address)
        self.instructions = instructions

    def get_instructions(self) -> list:
        return self.instructions

    def bytes(self, assembler=None):
        if assembler is None:
            assembler = Assembler()

        return assembler.bytes(self)

    def __iter__(self):
        for i in self.instructions:
            yield i
