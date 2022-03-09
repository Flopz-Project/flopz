from typing import Callable

from flopz.arch.instruction import Instruction
from flopz.core.addressable_object import AddressableObject


class Label(AddressableObject):
    """
    A class for putting symbolic labels into your assembly
    """
    def __init__(self, name: str):
        super(Label, self).__init__(object_addr=0)
        # final will be True only if the Assembler has figured out the right position for this Label
        self.final = False
        self.name = name

    def ref(self, ins: Callable[[int], Instruction]):
        """
        :return: a LabelRef to this label
        """
        return LabelRef(self.name, ins)

    def finalize(self, addr: int):
        self.object_addr = addr
        self.final = True


class LabelRef(AddressableObject):
    """
    Wrap any instruction (or function), providing the address of a label once the label is resolved
    """
    def __init__(self, label_name: str, ins: Callable[[int], Instruction], addr: int = 0):
        super(LabelRef, self).__init__(object_addr=addr)
        self.label_name = label_name
        self.ins = ins

    def size(self):
        """
        :return: the size of the underlying instruction, in bytes
        """
        return self.ins(0).size_bytes()

    def resolve_with_label(self, label: Label) -> Instruction:
        return self.ins(label.get_relative_address(self.get_absolute_address()))


class AbsoluteLabelRef(LabelRef):
    """
    Same thing as LabelRef, but gives an absolute address instead of a relative one.
    """
    def resolve_with_label(self, label: Label) -> Instruction:
        return self.ins(label.get_absolute_address())