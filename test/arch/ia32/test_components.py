import pytest
from flopz.arch.ia32.instruction_components import *


def test_instruction_components():
    opcode = IA32Opcode(0x88, op_size=32)
    assert (opcode.encode() == b'\x88')
    opcode = IA32Opcode(0x88)
    assert (opcode.encode() == b'\x48\x88')  # added REX bite indicating w flag for operand size

    modrm = ModRM(rm=10, reg=2, opcode=opcode)
    assert (modrm.rm == 10)
    assert (modrm.reg == 2)
    assert (opcode.rex.b)  # b flag has to be set due to rm=10

