from flopz.arch.ppc.vle.instructions import *

def test_store_instructions():
    # 54 a4 80 20     e_stw      r5,-0x7fe0(r4)
    stw = EStw(5, 4, -0x7fe0)
    assert(stw.bytes() == b'\x54\xa4\x80\x20')

    # df 31           se_stw     r3,0xf(r1)
    stw = SeStw(3, 1, 0xf)
    assert(stw.bytes() == b'\xd3\x31')

    # dd 01           se_stw     r0,0xd(r1)
    stw = SeStw(0, 1, 0xd)
    assert(stw.bytes() == b'\xd3\x01')

    # b4 cb           se_sth     r28,0x4(r27)
    stw = SeSth(28, 27, 4)
    assert(stw.bytes() == b'\xb2\xcb')

    # 99 69           se_stb     r6,0x9(r25)
    stw = SeStb(6, 25, 9)
    assert(stw.bytes() == b'\x99\x69')


def test_load_instructions():
    # c7 f1           se_lwz     r31,0x7(r1)
    load = SeLwz(31, 1, 7)
    assert(load.bytes() == b'\xc1\xf1')

    # a5 0e           se_lhz     r0,0x5(r30)
    load = SeLhz(0, 30, 0x5)
    assert(load.bytes() == b'\xa2\x0e')

    # 88 34           se_lbz     r3,0x8(r4)
    load = SeLbz(3, 4, 8)
    assert(load.bytes() == b'\x88\x34')

def test_spr_movs():
    # 7c 7a 03 a6     mtspr      SRR0,r3 (SRR0 = 26)
    mov = Mtspr(26, 3)
    assert(mov.bytes() == b'\x7c\x7a\x03\xa6')

    # 7c 30 42 a6     mfspr      r1,SPRG0
    mov = Mfspr(1, 272)
    assert(mov.bytes() == b'\x7c\x30\x42\xa6')


def test_stmw():
    # 19 c1 09 38     e_stmw     r14,0x38(r1)
    store = EStmw(14, 1, 0x38)
    assert(store.bytes() == b'\x19\xc1\x09\x38')
