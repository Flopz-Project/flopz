from flopz.arch.ppc.ppc_generic_arch import PPCGenericArchitecture
from flopz.arch.ppc.vle.instructions import *


def test_control_flow_cmp():
    arch = PPCGenericArchitecture()

    # se_cmpi    r3,0x0
    cmp = SeCmpi(arch.r3, 0)
    assert(cmp.bytes() == b'\x2a\x03')

    # 2a 24           se_cmpi    r4,0x2
    cmp = SeCmpi(arch.r4, 0x2)
    assert(cmp.bytes() == b'\x2a\x24')

    # 22 f6           se_cmpli   r6,0x10
    cmp = SeCmpli(arch.r6, 0x10)
    assert(cmp.bytes() == b'\x22\xf6')

    # 22 60           se_cmpli   r0,0x7
    cmp = SeCmpli(arch.r0, 0x7)
    assert(cmp.bytes() == b'\x22\x60')



def test_arithmetic():
    arch = PPCGenericArchitecture()

    # 20 06           se_addi    r6,0x1
    add = SeAddi(arch.r6, 0x1)
    assert(add.bytes() == b'\x20\x06')

    # 24 3f           se_subi    r31,0x4
    sub = SeSubi(arch.r31, 0x4)
    assert(sub.bytes() == b'\x24\x3f')
    assert(sub.OIM5().int == 0x4)
