
from flopz.arch.register import Register


class Architecture:
    """ An architecture is a combination of a set of registers and its compatible instructions.

    One can sub-class architectures in order to refine.
    For example, it is legit to subclass an architecture for a particular MCU core
    """
    def __init__(self, register_class=Register):
        self.register_class = register_class
        # to be filled by subclass
        self.registers = []
        self.instructions = []