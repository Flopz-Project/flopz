from flopz.arch.register import Register
from flopz.arch.ppc.ppc_generic_arch import PPCGenericArchitecture


def test_register_presence():
    # it should have all general purpose registers defined
    arch = PPCGenericArchitecture()
    assert(len(arch.registers) == 33)

    # registers should be of class Register (the base class)
    assert(type(arch.registers[0]) == Register)