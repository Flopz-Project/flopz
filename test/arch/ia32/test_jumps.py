import pytest
from flopz.arch.ia32.ia32_generic_arch import IA32GenericArchitecture
from flopz.arch.ia32.auto_instructions import *


def test_unconditional_jumps():
    arch = IA32GenericArchitecture()

    jmp = Jmp(arch.r10)
    assert(jmp.bytes() == b'\x41\xff\xe2')

    jmp = Jmp(arch.ma(64, arch.rbx + 32))
    assert(jmp.bytes() == b'\xff\x63\x20')

    jmp = Jcc(Cond.NZ, 0x200)
    assert(jmp.bytes() == b'\x0f\x85\x00\x02\x00\x00')

    jmp = Jcc(Cond.B, 0x12)
    assert(jmp.bytes() == b'\x72\x12')
