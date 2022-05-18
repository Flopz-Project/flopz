from flopz.arch.ia32.ia32_generic_arch import IA32GenericArchitecture
from flopz.arch.ia32.auto_instructions import *


def test_logic():
    arch = IA32GenericArchitecture()

    and_ins = AND(arch.cl, 5)
    assert(and_ins.bytes() == b"\x80\xe1\x05")
    or_ins = OR(arch.bl, 2)
    assert(or_ins.bytes() == b'\x80\xcb\x02')
    xor_ins = XOR(arch.rdx, 0x2365)
    assert(xor_ins.bytes() == b'\x48\x81\xf2\x65\x23\x00\x00')

    and_ins = AND(arch.r10, arch.ma(64, arch.rsi + arch.rdx * 4))
    assert(and_ins.bytes() == b'\x4c\x23\x14\x96')
    