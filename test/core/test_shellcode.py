from flopz.core.shellcode import Shellcode
from flopz.arch.ppc.vle.e200z0 import E200Z0
from flopz.arch.ppc.vle.instructions import *


def test_basic_shellcode():
    # it should be an AddressableObject
    s = Shellcode()
    assert(s.object_addr == 0)

    # it should keep a list of instructions
    assert(len(s.instructions) == 0)
    assert(s.get_instructions() == s.instructions)

    # it provides a helper method for assembling its instructions
    assert(s.bytes() == b'')

    # it provides a method to iterate over all instructions
    arch = E200Z0()
    s = Shellcode(instructions=[
        SeAdd(arch.r0, arch.r1),
        SeB(0),
    ])
    assert(any(s))
    assert(all([isinstance(ins, Instruction) for ins in s]))

