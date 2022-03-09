from flopz.arch.arm.thumb.instructions import *
from flopz.arch.arm.arm_generic_arch import ARMGenericArchitecture

def test_arithmetic():
    arch = ARMGenericArchitecture()
    addsI = AddI_T1(arch.r6, arch.r3, 1)
    assert(addsI.opcode() == BitArray(bin='0001110'))
    assert(addsI.imm3().uint == 1)
    assert(addsI.Rn().uint == 3)
    assert(addsI.Rd().uint == 6)
    assert(addsI.bytes() == b'\x5e\x1c')

    addw = AddI_T3(arch.r4, arch.r4, 0x400000, setflags=1)
    assert(addw.bytes() == b'\x14\xf5\x80\x04')
    addw = AddI_T3(arch.r4, arch.r4, 0x32)
    assert(addw.bytes() == b'\x04\xf1\x32\x04')

    addsR = AddsR(3, 4, 1)
    assert(addsR.opcode() == BitArray(bin='0001100'))
    assert(addsR.Rm().uint == 1)
    assert(addsR.Rn().uint == 4)
    assert(addsR.Rd().uint == 3)
    assert(addsR.bytes() == b'\x63\x18')

    subsR = SubsR(4, 2, 1)
    assert(subsR.opcode() == BitArray(bin='0001101'))
    assert(subsR.Rm().uint == 1)
    assert(subsR.Rn().uint == 2)
    assert(subsR.Rd().uint == 4)
    assert(subsR.bytes() == b'\x54\x1a')

    subsI = SubI_T1(2, 3, 1)
    assert(subsI.opcode() == BitArray(bin='0001111'))
    assert(subsI.imm3().uint == 1)
    assert(subsI.Rn().uint == 3)
    assert(subsI.Rd().uint == 2)
    assert(subsI.bytes() == b'\x5a\x1e')

    subw = SubI_T3(arch.r4, arch.r1, 0x1000)
    assert(subw.bytes() == b'\xa1\xf5\x80\x54')


def test_move_and_shifts():
    mov = MovT1(5, 1)
    assert(mov.opcode() == BitArray(bin='01000110'))
    assert(mov.Rm().uint == 1)
    assert(mov.Rdn().uint == 5)
    assert(mov.bytes() == b'\x0d\x46')

    lsl = LslsI(2, 2, 0x1b)
    assert(lsl.opcode() == BitArray(bin='00000'))
    assert(lsl.Rd().uint == 2)
    assert(lsl.Rm().uint == 2)
    assert(lsl.imm5().uint == 0x1b)
    assert(lsl.bytes() == b'\xd2\x06')

    lsr = LsrsI(3, 1, 0x10)
    assert(lsr.opcode() == BitArray(bin='00001'))
    assert(lsr.Rm().uint == 1)
    assert(lsr.Rd().uint == 3)
    assert(lsr.imm5().uint == 16)
    assert(lsr.bytes() == b'\x0b\x0c')


def test_branches():
    cb = B_T1(Cond.CC, -28)
    assert(cb.opcode() == BitArray(bin='1101'))
    assert(cb.cond().uint == 3)
    assert(cb.imm8().int == -16)
    assert(cb.offset() == -28)
    assert(cb.bytes() == b'\xf0\xd3')

    cb2 = B_T1(Cond.HI, -8)
    assert(cb2.opcode() == BitArray(bin='1101'))
    assert(cb2.cond().uint == Cond.HI)
    assert(cb2.offset() == -8)
    assert(cb2.bytes() == b'\xfa\xd8')

    ub = B_T2(0)
    assert(ub.opcode() == BitArray(bin='11100'))
    assert(ub.offset() == 0)
    assert(ub.bytes() == b'\xfe\xe7')

    ub2 = B_T2(-10)
    assert(ub2.opcode() == BitArray(bin='11100'))
    assert(ub2.offset() == -10)
    assert(ub2.bytes() == b'\xf9\xe7')

    bccw = B_T3(Cond.CC, -0x176)
    assert(bccw.opcode() == BitArray(bin='11110100'))
    assert(bccw.cond().uint == Cond.CC)
    assert(bccw.offset() == -0x176)
    assert(bccw.encoding() == BitArray(bin='11111111111101000011'))
    assert(bccw.bytes() == b'\xff\xf4\x43\xaf')

    bw = B_T4(-0x40)
    assert(bw.opcode() == BitArray(bin='11110101'))
    assert(bw.offset() == -0x40)
    assert(bw.encoding() == BitArray(bin='111111111111111111011110'))
    assert(bw.bytes() == b'\xff\xf7\xde\xbf')

    bw2 = B_T4(0x18e0 - 0xf10)
    assert(bw2.opcode() == BitArray(bin='11110101'))
    assert(bw2.offset() == 2512)
    assert(bw2.encoding() == BitArray(bin='000000000000010011100110'))
    assert(bw2.bytes() == b'\00\xf0\xe6\xbc')

    bl = BL_T1(0x13f6)
    assert(bl.opcode() == BitArray(bin="11110111"))
    assert(bl.offset() == 0x13f6)
    assert(bl.bytes() == b'\x01\xf0\xf9\xf9')


def test_it():
    itne = IT(Cond.NE, '')
    assert(itne.opcode() == BitArray(bin='10111111'))
    assert(itne.cond().uint == Cond.NE)
    assert(itne.mask().uint == 8)
    assert(itne.bytes() == b'\x18\xbf')

    itttteq = IT(Cond.EQ, 'TTT')
    assert(itttteq.opcode() == BitArray(bin='10111111'))
    assert(itttteq.cond().uint == Cond.EQ)
    assert(itttteq.mask().uint == 1)
    assert(itttteq.bytes() == b'\x01\xbf')

    itecc = IT(Cond.CC, 'E')
    assert (itecc.opcode() == BitArray(bin='10111111'))
    assert (itecc.cond().uint == Cond.CC)
    assert (itecc.mask().uint == 4)
    assert(itecc.bytes() == b'\x34\xbf')


def test_store_loads():

    # immediates
    stri = Str(5, 0, 0x28)
    assert(stri.opcode() == BitArray(bin='01100'))
    assert(stri.Rt().uint == 5)
    assert(stri.Rn().uint == 0)
    assert(stri.imm5().uint == 10)
    assert(stri.bytes() == b'\x85\x62')

    ldri = Ldr(3, 7, 0x4)
    assert(ldri.opcode() == BitArray(bin='01101'))
    assert(ldri.Rt().uint == 3)
    assert(ldri.Rn(). uint == 7)
    assert(ldri.imm5().uint == 1)
    assert(ldri.bytes() == b'\x7b\x68')

    strw = StrW(7, 2, 0x4, index=True, wback=True)
    assert(strw.opcode() == BitArray(bin='1111100001001'))
    assert(strw.Rt().uint == 7)
    assert(strw.Rn().uint == 2)
    assert(strw.imm8().uint == 4)
    assert(strw.bytes() == b'\x42\xf8\x04\x7f')

    ldrw12 = LdrWI12(3, 4, 0x10c)
    assert(ldrw12.opcode() == BitArray(bin='111110001101'))
    assert(ldrw12.Rt().uint == 3)
    assert(ldrw12.Rn().uint == 4)
    assert(ldrw12.imm12().uint == 0x10c)
    assert(ldrw12.bytes() == b'\xd4\xf8\x0c\x31')

    ldrliteral = LdrWLit(12, 8)
    assert(ldrliteral.opcode() == BitArray(bin='111110001011111'))
    assert(ldrliteral.Rt().uint == 12)
    assert(ldrliteral.imm12().uint == 8)
    assert(ldrliteral.U().uint == 1)
    assert(ldrliteral.bytes() == b'\xdf\xf8\x08\xc0')

    # registers
    strreg = StrWR(3, 10, 7)
    assert(strreg.opcode() == BitArray(bin='1111100001000'))
    assert(strreg.Rt().uint == 3)
    assert(strreg.Rn().uint == 10)
    assert(strreg.Rm().uint == 7)
    assert(strreg.shift().uint == 0)
    assert(strreg.bytes() == b'\x4a\xf8\x07\x30')

    ldrreg = LdrWR(0, 3, 0, shift=2)
    assert(ldrreg.opcode() == BitArray(bin='1111100001010'))
    assert(ldrreg.Rt().uint == 0)
    assert(ldrreg.Rn().uint == 3)
    assert(ldrreg.Rm().uint == 0)
    assert(ldrreg.shift().uint == 2)
    assert(ldrreg.bytes() == b'\x53\xf8\x20\x00')

# TODO test byte and halfword modes


def test_store_load_multiple():
    stmia = Stmia(5, [0, 1, 2, 3])
    assert(stmia.opcode() == BitArray(bin='11000'))
    assert(stmia.Rn().uint == 5)
    assert(stmia.bytes() == b'\x0f\xc5')

    ldmia = Ldmia(3, [1, 2, 3])
    assert(ldmia.opcode() == BitArray(bin='11001'))
    assert(ldmia.Rn().uint == 3)
    assert(ldmia.bytes() == b'\x0e\xcb')

    stmiaw = StmiaW(4, [0, 1, 2, 3])
    assert(stmiaw.opcode() == BitArray(bin='111010001000'))
    assert(stmiaw.Rn().uint == 4)
    assert(stmiaw.bytes() == b'\x84\xe8\x0f\x00')

    ldmiaw = LdmiaW(0, list(range(12)))
    assert(ldmiaw.opcode() == BitArray(bin='111010001001'))
    assert(ldmiaw.Rn().uint == 0)
    assert(ldmiaw.bytes() == b'\x90\xe8\xff\x0f')


def test_logicals():
    ands = Ands(3, 2)
    assert(ands.bytes() == b'\x13\x40')

    orrs = Orrs(2, 3)
    assert(orrs.bytes() == b'\x1a\x43')

    eors = Eors(2, 1)
    assert(eors.bytes() == b'\x4a\x40')

    andw = AndI(3, 3, 0x10000000)
    assert(andw.bytes() == b'\x03\xf0\x80\x53')

    orrw = OrrI(3, 3, 0x5f80000)
    assert(orrw.bytes() == b'\x43\xf0\xbf\x63')

    eorw = EorI(3, 3, 0x100000)
    assert(eorw.bytes() == b'\x83\xf4\x80\x13')


def test_misc():
    ux = UXTB(3, 3)
    assert(ux.bytes() == b'\xdb\xb2')

    arch = ARMGenericArchitecture()

    pop = POP([arch.r7, arch.pc])
    assert(pop.bytes() == b'\x80\xbd')

    push = PUSH([arch.r7, arch.lr])
    assert(push.bytes() == b'\x80\xb5')


