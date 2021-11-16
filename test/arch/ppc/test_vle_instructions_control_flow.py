from flopz.arch.ppc.ppc_generic_arch import PPCGenericArchitecture
from flopz.arch.ppc.vle.instructions import *


def test_control_flow_cmp():
    arch = PPCGenericArchitecture()

    # 78 00 02 18     e_b
    branch = EB(0x218)
    assert(branch.bytes() == b'\x78\x00\x02\x18')

    # 79 ff f7 21     e_bl
    branch = EBl(-0x8e0)
    assert(branch.bytes() == b'\x79\xff\xf7\x21')

    #  e8 08           se_b
    branch = SeB(0x10)
    assert(branch.bytes() == b'\xe8\x08')

    #  e9 c7           se_bl
    branch = SeBl(-0x72)
    assert(branch.bytes() == b'\xe9\xc7')

    # conditional branches
    #  7a 12 fe d6     e_beq
    branch = EBe(-0x12a)
    assert(branch.bytes() == b'\x7a\x12\xfe\xd6')

    # 7a 02 04 1a     e_bne
    branch = EBne(0x41a)
    assert(branch.bytes() == b'\x7a\x02\x04\x1a')

    # 7a 11 04 02 e_bgt
    branch = EBgt(0x402)
    assert(branch.bytes() == b'\x7a\x11\x04\x02')

    # e_blt
    # 7a 10 00 e8     e_blt
    branch = EBlt(0xe8)
    assert(branch.bytes() == b'\x7a\x10\x00\xe8')

    # se_beq
    # e6 0e           se_beq
    branch = SeBeq(0x1c)
    assert(branch.bytes() == b'\xe6\x0e')

    # se_bne
    # e2 f9           se_bne
    branch = SeBne(-0xe)
    assert(branch.bytes() == b'\xe2\xf9')

    # se_blt
    # e4 02           se_blt
    branch = SeBlt(0x4)
    assert(branch.bytes() == b'\xe4\x02')

    # se_bgt
    # e5 07           se_bgt
    branch = SeBgt(0xe)
    assert(branch.bytes() == b'\xe5\x07')

def test_branch_ctr_and_link():
    # 00 04           se_blr
    branch = SeBlr()
    assert (branch.bytes() == b'\x00\x04')

    # 00 05           se_blrl
    branch = SeBlrl()
    assert (branch.bytes() == b'\x00\x05')

    # 00 06           se_bctr
    branch = SeBctr()
    assert (branch.bytes() == b'\x00\x06')

    # 00 07           se_bctrl
    branch = SeBctrl()
    assert (branch.bytes() == b'\x00\x07')