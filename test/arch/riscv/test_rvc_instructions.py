from flopz.arch.riscv.rv32c.instructions import *
from flopz.arch.riscv.riscv_generic_arch import RiscvGenericArchitecture


def test_loads_and_stores():
    ar = RiscvGenericArchitecture()

    assert(CLWSP(ar.ra, 0xC).bytes() == b'\xb2\x40')
    assert(CSWSP(ar.ra, 0xC).bytes() == b'\x06\xc6')
    assert(CLW(ar.a4, ar.a1, 0x4).bytes() == b'\xd8\x41')
    assert(CSW(ar.a4, ar.a3, 0xc).bytes() == b'\xd8\xc6')


def test_jumps_and_breaks():
    ar = RiscvGenericArchitecture()

    assert(CJ(-0x9c).bytes() == b'\x95\xb7')
    # no code snipped found for JAL
    assert (CJAL(-0x9c).bytes() == b'\x95\x37')
    assert(CJR(ar.t1).bytes() == b'\x02\x83')
    assert(CJALR(ar.a5).bytes() == b'\x82\x97')

    assert(CBEQZ(ar.a5, 0x12).bytes() == b'\x89\xcb')
    assert(CBNEZ(ar.a3, 0xb4).bytes() == b'\xd5\xea')


def test_constant_generators():
    ar = RiscvGenericArchitecture()

    assert(CLI(ar.a7, 0x18).bytes() == b'\xe1\x48')
    assert(CLUI(ar.a5, 0x10000).bytes() == b'\xc1\x67')


def test_register_immediate_operations():
    ar = RiscvGenericArchitecture()

    assert(CADDI(ar.a3, -0x2).bytes() == b'\xf9\x16')
    assert(CADDI16SP(-0x30).bytes() == b'\x79\x71')
    assert(CADDI4SPN(ar.a5, 0x24).bytes() == b'\x5c\x10')

    assert(CSLLI(ar.a5, 0x3).bytes() == b'\x8e\x07')
    assert(CSRLI(ar.a4, 0x1b).bytes() == b'\x6d\x83')
    # no code for C.SRAI found
    assert(CSRAI(ar.a4, 0x1b).bytes() == b'\x6d\x87')

    assert(CANDI(ar.a5, 0x8).bytes() == b'\xa1\x8b')


def test_register_register_operations():
    ar = RiscvGenericArchitecture()

    assert(CMV(ar.a0, ar.s0).bytes() == b'\x22\x85')
    assert(CADD(ar.a7, ar.a3).bytes() == b'\xb6\x98')

    assert(CAND(ar.a3, ar.a5).bytes() == b'\xfd\x8e')
    assert(COR(ar.a1, ar.a5).bytes() == b'\xdd\x8d')
    assert(CXOR(ar.a0, ar.a5).bytes() == b'\x3d\x8d')

    assert(CSUB(ar.a0, ar.a5).bytes() == b'\x1d\x8d')


def test_nop_and_break():
    assert(CNOP().bytes() == b'\x01\x00')
    assert(CEBREAK().bytes() == b'\x02\x90')
