import typing
from typing import List, Callable

from flopz.core.shellcode import Shellcode


class Module(Shellcode):
    """
    A Module is a piece of shellcode that describes which registers it uses
    Modules can be parameterized. Subclasses can define extra parameters that have to be filled
    Modules should be composable (SequentialModule consists of multiple Modules which are executed in sequence etc.)
    """
    def __init__(self, address: int, instructions: list = [], registers_written: list = [],
                 registers_read: list = [], instructions_func: Callable = None, instructions_args: dict = None):
        super(Module, self).__init__(instructions=instructions, address=address)
        self._registers_written = registers_written
        self._registers_read = registers_read
        self.instructions_func = instructions_func
        self.instructions_args = instructions_args

    def registers_written(self) -> list:
        return self._registers_written

    def registers_read(self) -> list:
        return self._registers_read

    def bytes(self, assembler=None, instruction_args: dict = None):
        if self.instructions_func:
            if instruction_args:
                self.instructions_args = instruction_args
            self.instructions = self.instructions_func(self.instructions_args)
        return super(Module, self).bytes(assembler)


class SequentialModule(Module):
    """
    use this module to compose several other modules and assemble them sequentially
    """
    def __init__(self, address: int, modules: List[Module]):
        super(SequentialModule, self).__init__(address=address)
        self.modules = modules

    def registers_read(self) -> list:
        """
        :return: aggregate list of all registers read by submodules
        """
        regs = []
        for m in self.modules:
            for r in m.registers_read():
                if r not in regs:
                    regs.append(r)
        return regs

    def registers_written(self) -> list:
        """
        :return: aggregate list of all registers written to by submodules
        """
        regs = []
        for m in self.modules:
            for r in m.registers_written():
                if r not in regs:
                    regs.append(r)
        return regs


    def bytes(self, assembler=None):
        return b''.join([m.bytes() for m in self.modules])
