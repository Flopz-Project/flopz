import pytest
from flopz.arch.ia32.ia32_generic_arch import IA32GenericArchitecture
from flopz.arch.ia32.auto_instructions import *


def test_shifts():
    arch = IA32GenericArchitecture()

    shl = SHL(arch.r12, 5)
    assert(shl.bytes() == b'\x49\xc1\xe4\x05')

    shl = SHL(arch.dl, 1)
    assert(shl.bytes() == b'\xd0\xe2')

    with pytest.raises(ValueError):
        SHL(arch.eax, 51)

    sal = SAL(arch.ma(64, arch.rdx + arch.rbx * 2 - 12), 31)
    assert(sal.bytes() == b'\x48\xc1\x64\x5a\xf4\x1f')

    sal = SAL(arch.r15b, arch.cl)
    assert(sal.bytes() == b'\x41\xd2\xe7')

    with pytest.raises(ValueError):
        SAL(arch.r15b, arch.ah)

    shr = SHR(arch.rcx, 2)
    assert(shr.bytes() == b'\x48\xc1\xe9\x02')

    sar = SAR(arch.si, arch.cl)
    assert(sar.bytes() == b'\x66\xd3\xfe')
