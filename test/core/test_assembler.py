from typing import List
import struct

from flopz.arch.auto_instruction import AutoInstruction
from flopz.arch.instruction import ArbitraryBytesInstruction
from flopz.core.shellcode import Shellcode
from flopz.core.assembler import Assembler
from flopz.arch.ppc.vle.e200z0 import E200Z0
from flopz.arch.ppc.vle.instructions import *
from flopz.core.label import Label, LabelRef, AbsoluteLabelRef
from pytest import raises


def test_basic_assembler():
    # it should assemble plain instructions
    arch = E200Z0()
    ins1 = SeAdd(arch.r0, arch.r1)
    ins2 = SeB(0)
    s = Shellcode(instructions=[
        ins1,
        ins2
    ])
    assert(s.bytes() == (ins1.bytes() + ins2.bytes()))

    # it should expand auto instructions
    class Bla(AutoInstruction):
        def expand(self) -> List[Instruction]:
            return [ArbitraryBytesInstruction(b'\x42\x42'), ArbitraryBytesInstruction(b'\x24\x24')]

    s = Shellcode(instructions=[Bla()])
    assert(s.bytes() == b'\x42\x42\x24\x24')


def test_label_resolution():
    # it should resolve backward label references
    arch = E200Z0()
    ins1 = SeAdd(arch.r0, arch.r1)
    ins2 = SeB(0)
    s = Shellcode(instructions=[
        Label("testLabel"),
        ins1,
        ins2,
        LabelRef("testLabel", SeB)
    ], address=0)
    comparison = SeB(-4)
    result = s.bytes()
    assert(result[-2:] == comparison.bytes())

    # it should resolve forward label references
    s = Shellcode(instructions=[
        LabelRef("testLabel", SeB),
        ins1,
        ins2,
        Label("testLabel"),
    ], address=0)
    comparison = SeB(6)
    result = s.bytes()
    assert(result[:2] == comparison.bytes())

    # it should err on references to unknown labels
    s = Shellcode(instructions=[
        LabelRef("testLabel", SeB),
        ins1,
    ], address=0)
    with raises(Exception):
        result = s.bytes()

    # it should resolve absoluteLabelRefs
    def test_get_addr(a):
        return ArbitraryBytesInstruction(bytes=struct.pack('I', a))

    s = Shellcode(instructions=[
        AbsoluteLabelRef("testLabel", test_get_addr),
        ArbitraryBytesInstruction(b'\x00' * 16),
        Label("testLabel"),
    ], address=0)
    result = s.bytes()
    assert(struct.unpack('I', result[0:4])[0] == 20)