import pytest
from flopz.arch.ia32.ia32_generic_arch import IA32GenericArchitecture
from flopz.arch.ia32.addressing import MemoryAddress


def test_memaddr():
    arch = IA32GenericArchitecture()

    with pytest.raises(ValueError):
        ma = arch.r12 + 2**32

    ma = arch.r12 - 137
    assert(ma.displacement == -137)
    assert(ma.base == arch.r12)

    with pytest.raises(ValueError):
        ma = arch.r10 * 7
    ma = arch.r10 * 8
    assert(ma.index == arch.r10)
    assert(ma.scale == 8)

    assert(isinstance(arch.ma(16, arch.rax), MemoryAddress))
    with pytest.raises(ValueError):
        isinstance(arch.ma(15, arch.rax), MemoryAddress)

