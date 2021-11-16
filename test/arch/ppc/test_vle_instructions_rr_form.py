from flopz.arch.ppc.vle.instructions import *


def test_arithmetic():
    add = SeAdd(4, 0) # se_add r4, r0
    assert(add.opcode.uint == 0x1)
    assert(add.RY().uint == 0)
    assert(add.RX().uint == 4)
    # it should encode
    assert(add.bytes() == b'\x04\x04')

    #  06 35           se_sub     r5,r3
    sub = SeSub(5, 3)
    assert(sub.bytes() == b'\x06\x35')

    # 05 70           se_mullw   r0,r7
    mul = SeMullw(0, 7)
    assert(mul.bytes() == b'\x05\x70')


def test_movs():
    # 01 43           se_mr      r3,r4
    mov = SeMr(3, 4)
    assert(mov.bytes() == b'\x01\x43')

    # 02 61           se_mtar    r9,r6
    mov = SeMtar(9, 6)
    assert(mov.bytes() == b'\x02\x61')

    # 03 14           se_mfar    r4,r9
    mov = SeMfar(4, 9)
    assert(mov.bytes() == b'\x03\x14')

    # 00 90           se_mtlr    r0
    mov = SeMtlr(0)
    assert(mov.bytes() == b'\x00\x90')

    # 00 80           se_mflr    r0
    mov = SeMflr(0)
    assert(mov.bytes() == b'\x00\x80')

    # 00 b7           se_mtctr   r7
    mov = SeMtctr(7)
    assert(mov.bytes() == b'\x00\xb7')

    # 00 a3           se_mfctr   r3
    mov = SeMfctr(3)
    assert(mov.bytes() == b'\x00\xa3')


def test_control_flow_cmp():
    # se_cmp
    # 0c b0           se_cmp     r0,r27
    cmp = SeCmp(0, 27)
    assert(cmp.bytes() == b'\x0c\xb0')

    # se cmpl
    # 0d 74           se_cmpl    r4,r7
    cmp = SeCmpl(4, 7)
    assert(cmp.bytes() == b'\x0d\x74')

    # se cmph
    # 0e 53           se_cmph    r3,r5
    cmp = SeCmph(3, 5)
    assert(cmp.bytes() == b'\x0e\x53')
