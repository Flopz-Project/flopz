from flopz.arch.ppc.vle.instructions import *

def test_wrteei():
    #  7c 00 01 46     wrteei     0x0
    op = Wrteei(0)
    assert(op.bytes() == b'\x7c\x00\x01\x46')

    #  7c 00 81 46     wrteei     0x1
    op = Wrteei(1)
    assert(op.bytes() == b'\x7c\x00\x81\x46')



def test_mt_mf_cr():
    # 7c 6f f1 20     mtcrf      0xff,r3
    op = Mtcrf(0xFF, 3)
    assert(op.bytes() == b'\x7c\x6f\xf1\x20')

    # 7c 60 00 26     mfcr       r3
    op = Mfcr(3)
    assert(op.bytes() == b'\x7c\x60\x00\x26')

    # 7f 60 00 26     mfcr       r27
    op = Mfcr(27)
    assert(op.bytes() == b'\x7f\x60\x00\x26')