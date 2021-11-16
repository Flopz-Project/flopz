from typing import List

from flopz.arch.instruction import Instruction
from flopz.core.module import Module


class Function(Module):
    """
    A Function is a Module that can be called without having to manually clean registers
    In general, there should be no need to subclass this as any module can be wrapped by this class
    You can, however, subclass Function in order to provide cleaner syntax for often-used Functions
    For example, it might make sense to create a PPCFunction, where only the logic has to be provided and the other modules are static
    Simply pass the individual modules and enjoy
    """
    def __init__(self, address: int, save_register_module: Module, restore_register_module: Module,
                 logic: Module, make_call: Module = None):
        """

        :param address: target address for this function
        :param save_register_module: a module that generates code for saving one or more registers
        :param restore_register_module: a module that generates code for restoring one or more registers
        :param logic: module that contains this function's logic
        :param make_call: module that creates a call to this function
        """
        super(Function, self).__init__(address=address)
        self.save_register_module = save_register_module
        self.restore_register_module = restore_register_module
        self.logic = logic
        self.make_call = make_call


    def bytes(self, assembler=None, instruction_args: dict = None) -> bytes:
        # get main logic modified registers
        regs_to_save = self.logic.registers_written()
        # insert any extra args, if there are any
        extra_args = {}
        if instruction_args:
            extra_args = instruction_args

        # get code to save all the registers
        ret = self.save_register_module.bytes(instruction_args={'registers': regs_to_save} | extra_args)
        ret += self.logic.bytes()
        # add epilogue: restore all the registers again
        ret += self.restore_register_module.bytes(instruction_args={'registers': regs_to_save})
        return ret

    def get_call_instructions(self) -> List[Instruction]:
        pass

    def get_call_bytes(self) -> bytes:
        return self.make_call.bytes()

