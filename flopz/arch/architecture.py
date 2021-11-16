"""
an arch is a combination of
- a set of registers
- its compatible instructions

one can sub-class architectures in order to refine
for example, it is legit to subclass an architecture for a particular MCU core
"""
from flopz.arch.register import Register

class Architecture:
    def __init__(self, register_class=Register):
        self.register_class = register_class
        # to be filled by subclass
        self.registers = []
        self.instructions = []