from flopz.arch.riscv.rv32i.instructions import *
from flopz.arch.riscv.rv32i.rv32i_arch import RV32IArch


def test_ri_instructions():
    arch = RV32IArch()

    assert(R32iADDI(arch.t0, arch.t0, -0x454).bytes() == b'\x93\x82\xc2\xba')
    # MV is ADD with 0
    assert(R32iADDI(arch.t1, arch.zero, 0).bytes() == b'\x13\x03\x00\x00')
    assert(R32iADDI(arch.a0, arch.sp, 0).bytes() == b'\x13\x05\x01\x00')

    assert(R32iAUIPC(arch.ra, 0).bytes() == b'\x97\x00\x00\x00')
    assert(R32iAUIPC(arch.t2, 0x5000).bytes() == b'\x97\x53\x00\x00')

    assert(R32iLUI(arch.t2, -0x80000000).bytes() == b'\xb7\x03\x00\x80')
    assert(R32iLUI(arch.t0, -0x80000000).bytes() == b'\xb7\x02\x00\x80')

    assert(R32iSRAI(arch.a1, arch.a5, 0x1f).bytes() == b'\x93\xd5\xf7\x41')


def test_rr_instructions():
    arch = RV32IArch()
    assert(R32iAND(arch.a0, arch.a0, arch.t0).bytes() == b'\x33\x75\x55\x00')
    assert(R32iSRL(arch.a5, arch.a2, arch.a3).bytes() == b'\xb3\x57\xd6\x00')
    assert(R32iSLTU(arch.a5, arch.zero, arch.a5).bytes() == b'\xb3\x37\xf0\x00')


def test_unconditional_jumps():
    arch = RV32IArch()
    assert(R32iJAL(arch.ra, 0x9c).bytes() == b'\xef\x00\xc0\x09')
    assert(R32iJALR(arch.ra, arch.a5, 0x0).bytes() == b'\xe7\x80\x07\x00')


def test_conditional_branches():
    arch = RV32IArch()
    assert(R32iBEQ(arch.a6, arch.zero, 0x18).bytes() == b'\x63\x0c\x08\x00')
    assert(R32iBGEU(arch.a4, arch.a3, 0x1c).bytes() == b'\x63\x7e\xd7\x00')


def test_load_and_store():
    arch = RV32IArch()
    assert(R32iLW(arch.a5, arch.s0, 0x8).bytes() == b'\x83\x27\x84\x00')
    assert(R32iLW(arch.ra, arch.sp, 0x1c).bytes() == b'\x83\x20\xc1\x01')
    assert(R32iLHU(arch.a2, arch.a4, 0xe).bytes() == b'\x03\x56\xe7\x00')
    assert(R32iSB(arch.a5, -0xb, arch.s0).bytes() == b'\xa3\x0a\xf4\xfe')
    assert(R32iSW(arch.s0, 0x8, arch.sp).bytes() == b'\x23\x24\x81\x00')


def test_csr():
    arch = RV32IArch()
    assert (R32iCSRRCI(arch.s2, 0x5f7, 0x6).bytes() == b'\x73\x79\x73\x5f')
    assert (R32iCSRRC(arch.s0, arch.mstatus, arch.s5).bytes() == b'\x73\xb4\x0a\x30')



