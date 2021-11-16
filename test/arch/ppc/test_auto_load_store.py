from flopz.arch.ppc.vle.instructions import *
from flopz.arch.ppc.vle.auto_instructions import *

def test_auto_load():
    # test 7 bit immediate
    load = AutoLoadI(1, 0x3)
    instructions = load.expand()
    assert(type(instructions[0]) == SeLi)
    assert(len(instructions) == 1)
    assert(load.rD == 1)

    # test 20 bit signed immediate
    load = AutoLoadI(3, -0x7ff00)
    instructions = load.expand()
    assert(len(instructions) == 1)
    assert(type(instructions[0]) == ELi)
    assert(load.rD == 3)

    # test full 32 bit values, small low part
    load = AutoLoadI(3, 0x40020001)
    instructions = load.expand()
    assert(len(instructions) == 2)
    assert(type(instructions[0]) == ELis)
    assert(type(instructions[1]) == SeAddi)

    # test full 32 bit values, big low part (but lower than 0x8000)
    load = AutoLoadI(31, 0x40027fff)
    instructions = load.expand()
    assert(len(instructions) == 2)
    assert(type(instructions[0]) == ELis)
    assert(type(instructions[1]) == EAdd16i)

