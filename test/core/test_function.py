from flopz.core.function import Function
from flopz.core.module import Module, SequentialModule
from flopz.core.shellcode import Shellcode
from flopz.core.assembler import Assembler
from flopz.arch.ppc.vle.e200z0 import E200Z0
from flopz.arch.ppc.vle.instructions import *
from flopz.core.label import Label, LabelRef

from pytest import raises

def test_base_function():
    arch = E200Z0()
    # it should assemble in order: pre, logic, post
    pre_m = Module(address=0, instructions=[
        SeAdd(arch.r0, arch.r1),
    ], registers_written=[], registers_read=[])

    post_m = Module(address=0, instructions=[
        SeSubi(arch.r0, 1),
    ], registers_written=[], registers_read=[])
    logic = Module(address=0, instructions=[
        SeAdd(arch.r7, arch.r6),
    ], registers_written=[], registers_read=[])
    f = Function(address=0, save_register_module=pre_m, restore_register_module=post_m, logic=logic)
    assert(f.bytes() == (pre_m.bytes() + logic.bytes() + post_m.bytes()))

    # it should clean registers automatically, using the provided modules
    logic = Module(address=0, instructions=[
        SeAdd(arch.r7, arch.r6),
    ], registers_written=[arch.r0, arch.r1], registers_read=[])
    f = Function(address=0, save_register_module=Module(address=0, instructions_func=lambda conf: [
        *[SeSubi(reg, 1) for reg in conf['registers']]
    ]), restore_register_module=post_m, logic=logic)
    pre_bytes = SeSubi(arch.r0, 1).bytes() + SeSubi(arch.r1, 1).bytes()
    assert(f.bytes()[:len(pre_bytes)] == pre_bytes)




def test_extra_arguments():
    arch = E200Z0()
    # it should allow passing extra arguments via the bytes(..) call
    post_m = Module(address=0, instructions=[
        SeSubi(arch.r0, 1),
    ], registers_written=[], registers_read=[])
    logic = Module(address=0, instructions=[
        SeAdd(arch.r7, arch.r6),
    ], registers_written=[], registers_read=[])
    f = Function(address=0, save_register_module=Module(address=0, instructions_func=lambda conf: [
        *[SeSubi(reg, 1) for reg in conf['registers']]
    ]), restore_register_module=post_m, logic=logic)
    assert(f.bytes(instruction_args={'registers': []}) == (logic.bytes() + post_m.bytes()))