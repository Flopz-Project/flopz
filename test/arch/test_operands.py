from flopz.arch.instruction import Instruction
from flopz.arch.operands import Operand


def test_basic():
    ins = Instruction('', 0, 32)
    # it should reference the bits held by the instruction
    op = Operand(ins, 8, 13)
    op(31)
    assert(ins.bits[8:13].uint == 31)
    # it should allow to retrieve the value through calling
    assert(op().uint == 31)


