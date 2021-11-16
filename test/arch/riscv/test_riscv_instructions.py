from flopz.arch.riscv.rv32i.instructions import *
from flopz.arch.riscv.rv32i.rv32i_arch import RV32IArch


def test_ri_instructions():
    arch = RV32IArch()

    assert(ADDI(arch.t0, arch.t0, -0x454).bytes() == b'\x93\x82\xc2\xba')
    # MV is ADD with 0
    assert(ADDI(arch.t1, arch.zero, 0).bytes() == b'\x13\x03\x00\x00')
    assert(ADDI(arch.a0, arch.sp, 0).bytes() == b'\x13\x05\x01\x00')

    assert(AUIPC(arch.ra, 0).bytes() == b'\x97\x00\x00\x00')
    assert(AUIPC(arch.t2, 0x5000).bytes() == b'\x97\x53\x00\x00')

    assert(LUI(arch.t2, -0x80000000).bytes() == b'\xb7\x03\x00\x80')
    assert(LUI(arch.t0, -0x80000000).bytes() == b'\xb7\x02\x00\x80')

    assert(SRAI(arch.a1, arch.a5, 0x1f).bytes() == b'\x93\xd5\xf7\x41')


def test_rr_instructions():
    arch = RV32IArch()
    assert(AND(arch.a0, arch.a0, arch.t0).bytes() == b'\x33\x75\x55\x00')
    assert(SRL(arch.a5, arch.a2, arch.a3).bytes() == b'\xb3\x57\xd6\x00')
    assert(SLTU(arch.a5, arch.zero, arch.a5).bytes() == b'\xb3\x37\xf0\x00')


def test_unconditional_jumps():
    arch = RV32IArch()
    assert(JAL(arch.ra, 0x9c).bytes() == b'\xef\x00\xc0\x09')
    assert(JALR(arch.ra, arch.a5, 0x0).bytes() == b'\xe7\x80\x07\x00')


def test_conditional_branches():
    arch = RV32IArch()
    assert(BEQ(arch.a6, arch.zero, 0x18).bytes() == b'\x63\x0c\x08\x00')
    assert(BGEU(arch.a4, arch.a3, 0x1c).bytes() == b'\x63\x7e\xd7\x00')


def test_load_and_store():
    arch = RV32IArch()
    assert(LW(arch.a5, arch.s0, 0x8).bytes() == b'\x83\x27\x84\x00')
    assert(LW(arch.ra, arch.sp, 0x1c).bytes() == b'\x83\x20\xc1\x01')
    assert(LHU(arch.a2, arch.a4, 0xe).bytes() == b'\x03\x56\xe7\x00')
    assert(SB(arch.a5, -0xb, arch.s0).bytes() == b'\xa3\x0a\xf4\xfe')
    assert(SW(arch.s0, 0x8, arch.sp).bytes() == b'\x23\x24\x81\x00')


def test_csr():
    arch = RV32IArch()
    assert (CSRRCI(arch.s2, 0x5f7, 0x6).bytes() == b'\x73\x79\x73\x5f')
    assert (CSRRC(arch.s0, arch.mstatus, arch.s5).bytes() == b'\x73\xb4\x0a\x30')



