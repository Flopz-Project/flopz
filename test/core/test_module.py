from flopz.core.module import Module, SequentialModule
from flopz.core.shellcode import Shellcode
from flopz.core.assembler import Assembler
from flopz.arch.ppc.vle.e200z0 import E200Z0
from flopz.arch.ppc.vle.instructions import *
from flopz.core.label import Label, LabelRef

from pytest import raises

def test_base_module():
    arch = E200Z0()
    # it should accept instructions and a list of registers that are read from/written to by the code
    m = Module(address=0, instructions=[
        SeAdd(arch.r0, arch.r1),
    ], registers_written=[arch.r0], registers_read=[arch.r1])
    assert(len(m.instructions) == 1)
    assert(m.registers_read() == [arch.r1])
    assert(m.registers_written() == [arch.r0])

    # it should assemble, like shellcode
    assert(m.bytes() == SeAdd(arch.r0, arch.r1).bytes())


def test_sequential_module():
    arch = E200Z0()
    m1 = Module(address=0, instructions=[
        SeAdd(arch.r0, arch.r1),
    ], registers_written=[arch.r0], registers_read=[arch.r1])

    m2 = Module(address=0, instructions=[
        SeAdd(arch.r0, arch.r2),
    ], registers_written=[arch.r0], registers_read=[arch.r2])

    m = SequentialModule(address=0, modules=[
        m1,
        m2
    ])

    # it should provide an aggregate summary of all submodules' register usage
    assert(m.registers_read() == [arch.r1, arch.r2])
    assert(m.registers_written() == [arch.r0])

    m1_asm = m1.bytes()
    m2_asm = m2.bytes()

    # it should assemble its modules sequentially
    assert(m.bytes() == m1_asm + m2_asm)
    assert(m.bytes()[:len(m1_asm)]) == m1_asm


def test_parameterized_module():
    # it allows passing a function instead of pure instructions, along with parameters for that function
    arch = E200Z0()
    m1 = Module(address=0, instructions_func=lambda params: [
            SeAdd(arch.r0, arch.r1),
            *[SeAdd(arch.r0, reg) for reg in params['registers']]
        ], registers_written=[arch.r0], registers_read=[arch.r1],
                instructions_args={'registers': [arch.r1, arch.r2, arch.r3]})

    equiv_instructions = [SeAdd(arch.r0, reg) for reg in [arch.r1, arch.r2, arch.r3]]
    result = m1.bytes()
    assert(len(m1.instructions) == 4)
    assert(result[2:] == b''.join([x.bytes() for x in equiv_instructions]))

    # it allows passing different args to bytes()
    m1.bytes(instruction_args={'registers': [arch.r1]})
    assert(len(m1.instructions) == 2)