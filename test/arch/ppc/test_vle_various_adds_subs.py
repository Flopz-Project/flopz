from flopz.arch.ppc.vle.instructions import *

def test_eadd16i():
    # 1c 03 02 58     e_add16i   r0,r3,0x258
    add = EAdd16i(0, 3, 0x258)
    assert(add.bytes() == b'\x1c\x03\x02\x58')

    add = EAdd16i(26, 26, 0x74f8)
    assert(add.bytes() == b'\x1f\x5a\x74\xf8')

    # 1d ad ee a4     e_add16i   r13,r13,-0x115c
    add = EAdd16i(13, 13, -0x115c)
    assert(add.bytes() == b'\x1d\xad\xee\xa4')


def test_muls():
    # 70 00 a1 20     e_mull2i.  r0,0x120
    mul = EMull2i(0, 0x120)
    assert(mul.bytes() == b'\x70\x00\xa1\x20')
    assert(mul.SI().int == 0x120)

    # 70 0c a0 10     e_mull2i.  r12,0x10
    mul = EMull2i(12, 0x10)
    assert (mul.bytes() == b'\x70\x0c\xa0\x10')
    assert (mul.SI().int == 0x10)


def test_eadd2():
    # 73 e3 8f 80     e_add2i   r3, -0x80
    add = EAdd2i(3, -0x80)
    assert(add.bytes() == b'\x73\xe3\x8f\x80')
    assert(add.SI().int == -0x80)

    # 70 06 90 10     e_add2is   r6,0x10
    add = EAdd2is(6, 0x10)
    assert(add.bytes() == b'\x70\x06\x90\x10')