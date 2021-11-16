from flopz.arch.ppc.vle.instructions import *

def test_ands():
    # 2e 37           se_andi    r7,0x3
    op = SeAndi(7, 0x3)
    assert(op.bytes() == b'\x2e\x37')
    assert(op.UI5().uint == 0x3)

    # 70 18 c8 01     e_and2i.   r0,0xc001
    op = EAnd2i(0, 0xc001)
    assert(op.bytes() == b'\x70\x18\xc8\x01')
    assert(op.UI().uint == 0xc001)

    # 1b 40 c8 42     e_andi.    r0,r26,0x42
    op = EAndi_WithCR(0, 26, 0x42)
    assert(op.bytes() == b'\x1b\x40\xc8\x42')
    assert(op.RA().uint == 0)
    assert(op.UI().uint == 0x42)

    # 18 80 cb 8f     e_andi.    r0,r4,0x8f000000
    op = EAndi_WithCR(0, 4, 0x8f000000)
    assert(op.bytes() == b'\x18\x80\xcb\x8f')
    assert(op.RA().uint == 0)
    assert(op.RS().uint == 4)

    # 6c 6d           se_slwi    r29,0x6
    op = SeSlwi(29, 6)
    assert(op.bytes() == b'\x6c\x6d')

    # 68 57           se_srwi    r7,0x5
    op = SeSrwi(7, 5)
    assert(op.bytes() == b'\x68\x57')