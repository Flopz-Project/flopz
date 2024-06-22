from flopz.arch.ia32.ia32_generic_arch import IA32GenericArchitecture
from flopz.arch.ia32.auto_instructions import *
import pytest


def test_mov():
    arch = IA32GenericArchitecture()

    """ Reg to Reg """
    
    mov64 = Mov(arch.rax, arch.rbx)
    assert(mov64.bytes() == b'\x48\x89\xd8')
    assert(mov64.expand()[0].modrm._rm == 0)
    assert(mov64.expand()[0].modrm._reg == 3)

    mov64 = Mov(arch.r8, arch.r11)
    assert(mov64.bytes() == b'\x4D\x89\xd8')

    mov32 = Mov(arch.eax, arch.ebx)
    assert(mov32.bytes() == b'\x89\xd8')
    assert(mov32.expand()[0].modrm._rm == 0)
    assert(mov32.expand()[0].modrm._reg == 3)

    mov16 = Mov(arch.ax, arch.bx)
    assert(mov16.bytes() == b'\x66\x89\xd8')

    """ Reg to Mem """
    mov = Mov(arch.ma(64, arch.rax + arch.rbx * 4 - 64), arch.r12)
    assert(mov.bytes() == b'\x4c\x89\x64\x98\xc0')

    """ Mem to Reg """
    mov = Mov(arch.si, arch.ma(16, arch.r13 + arch.rbp * 8 - 107))
    assert(mov.bytes() == b'\x66\x41\x8B\x74\xED\x95')

    """ Imm to Reg """
    movi = Mov(arch.r12w, 28500)
    assert (movi.bytes() == b'\x66\x41\xBC\x54\x6f')
    movi2 = Mov(arch.rcx, 28500)
    assert (movi2.bytes() == b'\x48\xB9\x54\x6f\x00\x00\x00\x00\x00\x00')

    # it should correctly check the operand size
    with pytest.raises(Exception) as ex:
        Mov(arch.eax, 0xbdb4c444)
    assert("Immediate not fit for register" in ex.value.args)
    with pytest.raises(Exception) as ex:
        Mov(arch.ax, 0xfffff)
    assert("Immediate not fit for register" in ex.value.args)

    # this should work though:
    mov = Mov(arch.rbx, 0xbdb4c444)
    assert(mov.bytes() == b'\x48\xBB\x44\xC4\xB4\xBD\x00\x00\x00\x00')
    mov = Mov(arch.rax, -0xffffffff)
    assert(mov.bytes() == b'\x48\xB8\x01\x00\x00\x00\xFF\xFF\xFF\xFF')

    """ Imm to Mem """
    movi = Mov(arch.ma(32, arch.r13 + arch.rcx * 8 - 75), 0x10000000)
    assert(movi.bytes() == b'\x41\xc7\x44\xcd\xb5\x00\x00\x00\x10')
    movi2 = Mov(arch.ma(64, arch.r11 + arch.rcx*4 - 30), 0x10000000)
    assert(movi2.bytes() == b'\x49\xc7\x44\x8b\xe2\x00\x00\x00\x10')


def test_add():
    arch = IA32GenericArchitecture()

    """ Imm to Reg """
    addi = Add(arch.si, 32000)
    assert (addi.bytes() == b'\x66\x81\xc6\x00\x7d')
    addi = Add(arch.rdx, 0x2400)
    assert(addi.bytes() == b'\x48\x81\xc2\x00\x24\x00\00')

    """ Imm to Mem """
    addi = Add(arch.ma(8, arch.r14 + arch.rdi * 4 - 123), 2)
    assert(addi.bytes() == b'\x41\x80\x44\xbe\x85\x02')
    addi = Add(arch.ma(64, arch.r14 + arch.r10 * 8), 0x10203040)
    assert(addi.bytes() == b'\x4b\x81\x04\xd6\x40\x30\x20\x10')

    """ Reg to Reg """
    add = Add(arch.si, arch.r12w)
    assert(add.bytes() == b'\x66\x44\x01\xe6')

    """ Reg to Mem """
    add = Add(arch.ma(32, arch.r12 + arch.rcx * 8 - 99), arch.r8d)
    assert(add.bytes() == b'\x45\x01\x44\xcc\x9d')

    """ Mem to Reg """
    add = Add(arch.rcx, arch.ma(64, arch.r11 + arch.rdx*8 - 88))
    assert(add.bytes() == b'\x49\x03\x4c\xd3\xa8')




