from flopz.arch.ppc.vle.instructions import *

def test_e_li20():
    load = ELi(6, 0xc520)
    # 70 d8 05 20     e_li       r6,0xc520
    assert(load.bytes() == b'\x70\xd8\x05\x20')
    assert(load.I20().int == 0xc520)


def test_e_lis():
    # 71 a8 e0 02     e_lis      r13,0x4002
    load = ELis(13, 0x4002)
    assert(load.bytes() == b'\x71\xa8\xe0\x02')
    assert(load.UI().int == 0x4002)

def test_se_li():
    # 48 53           se_li      r3,0x5
    load = SeLi(3, 0x5)
    assert(load.bytes() == b'\x48\x53')
    assert(load.UI().int == 0x5)

def test_e_lmw():
    # 1b 41 08 48     e_lmw      r26,0x48(r1)
    load = ELmw(26, 1, 0x48)
    assert(load.bytes() == b'\x1b\x41\x08\x48')
    assert(load.RS().uint == 26)
    assert(load.D8().int == 0x48)
