from flopz.arch.ia32.ia32_generic_arch import IA32GenericArchitecture
from flopz.arch.ia32.instructions import *
import pytest


def test_mov():
    arch = IA32GenericArchitecture()

    mov64 = Mov(arch.rax, arch.rbx)
    assert(mov64.bytes() == b'\x48\x89\xd8')
    assert(mov64.rm() == 0)
    assert(mov64.reg() == 3)

    mov32 = Mov(arch.eax, arch.ebx)
    assert(mov32.bytes() == b'\x89\xd8')
    assert(mov32.rm() == 0)
    assert(mov32.reg() == 3)

    mov16 = Mov(arch.ax, arch.bx)
    assert(mov16.bytes() == b'\x66\x89\xd8')

    movi = Mov(arch.r12w, 28500)
    assert(movi.bytes() == b'\x66\x41\xBC\x54\x6f')
    movi2 = Mov(arch.rcx, 28500)
    assert(movi2.bytes() == b'\x48\xB9\x54\x6f\x00\x00\x00\x00\x00\x00')


def test_add():
    arch = IA32GenericArchitecture()

    addi = Add(arch.ebp, 20000)
    assert(addi.bytes() == b'\x81\xC5\x20\x4e\x00\x00')

    with pytest.raises(Exception):
        addr = Add(arch.ax, arch.ebx)

    addr = Add(arch.ax, arch.bx)
    assert(addr.bytes() == b'\x66\x03\xC3')


