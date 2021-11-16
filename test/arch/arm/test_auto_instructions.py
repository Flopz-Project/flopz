from flopz.arch.arm.thumb.auto_instructions import *


def test_auto_branch():
    ab_uncond1 = AutoBranch(0x20)
    ins = ab_uncond1.expand()[0]
    assert(ins.offset() == 0x20)
    assert(type(ins) == UB)

    assert(isinstance(Cond.NE, Enum))

    ab_cond1 = AutoBranch(0x20, Cond.NE)
    ins2 = ab_cond1.expand()[0]
    assert(ins2.offset() == 0x20)
    assert(ins2.cond().uint == Cond.NE)

    print(type(Cond.NE))
    ab_cond2 = AutoBranch(Cond.NE, 0x1cc)
    ins3 = ab_cond2.expand()[0]
    assert(ins2.cond() == ins3.cond())
    assert(ins3.offset() == 0x1cc)
    assert(type(ins2) == CB)
    assert(type(ins3) == CBW)

    ab_uncond2 = AutoBranch(-0xfffee)
    ins4 = ab_uncond2.expand()[0]
    assert(type(ins4) == UBW)


def test_auto_strldr():
    pass