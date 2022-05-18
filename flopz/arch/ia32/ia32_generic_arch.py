

from flopz.arch.architecture import Architecture
from flopz.arch.ia32.addressing import *

from flopz.arch.ia32.modes import ProcessorMode


class IA32GenericArchitecture(Architecture):
    """
    Higher-level architecture for IA-32 processors.

    Includes the general purpose (as 8, 16, 32 and 64 bit) and the segment registers as attributes.
    """
    def __init__(self, register_class=IA32Register, mode=ProcessorMode.LONG):
        super().__init__(register_class=register_class)

        self.mode = mode

        self.ma = MemoryAddressFactory()

        self.al = IA32Register("al", 0, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.ah = IA32Register("ah", 0, IA32RegType.GENERAL_PURPOSE, bit_size=8, is_high=True)
        self.cl = IA32Register("cl", 1, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.ch = IA32Register("ch", 1, IA32RegType.GENERAL_PURPOSE, bit_size=8, is_high=True)
        self.dl = IA32Register("dl", 2, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.dh = IA32Register("dh", 2, IA32RegType.GENERAL_PURPOSE, bit_size=8, is_high=True)
        self.bl = IA32Register("bl", 3, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.bh = IA32Register("bh", 3, IA32RegType.GENERAL_PURPOSE, bit_size=8, is_high=True)
        self.spl = IA32Register("spl", 4, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.bpl = IA32Register("bpl", 5, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.sil = IA32Register("sil", 6, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.dil = IA32Register("dil", 7, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r8b = IA32Register("r8b", 8, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r9b = IA32Register("r9b", 9, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r10b = IA32Register("r10b", 10, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r11b = IA32Register("r11b", 11, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r12b = IA32Register("r12b", 12, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r13b = IA32Register("r13b", 13, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r14b = IA32Register("r14b", 14, IA32RegType.GENERAL_PURPOSE, bit_size=8)
        self.r15b = IA32Register("r15b", 15, IA32RegType.GENERAL_PURPOSE, bit_size=8)

        self.ax = IA32Register("ax", 0, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.cx = IA32Register("cx", 1, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.dx = IA32Register("dx", 2, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.bx = IA32Register("bx", 3, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.sp = IA32Register("sp", 4, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.bp = IA32Register("bp", 5, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.si = IA32Register("si", 6, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.di = IA32Register("di", 7, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r8w = IA32Register("r8w", 8, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r9w = IA32Register("r9w", 9, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r10w = IA32Register("r10w", 10, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r11w = IA32Register("r11w", 11, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r12w = IA32Register("r12w", 12, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r13w = IA32Register("r13w", 13, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r14w = IA32Register("r14w", 14, IA32RegType.GENERAL_PURPOSE, bit_size=16)
        self.r15w = IA32Register("r15w", 15, IA32RegType.GENERAL_PURPOSE, bit_size=16)

        self.eax = IA32Register("eax", 0, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.ecx = IA32Register("ecx", 1, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.edx = IA32Register("edx", 2, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.ebx = IA32Register("ebx", 3, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.esp = IA32Register("esp", 4, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.ebp = IA32Register("ebp", 5, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.esi = IA32Register("esi", 6, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.edi = IA32Register("edi", 7, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r8d = IA32Register("r8d", 8, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r9d = IA32Register("r9d", 9, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r10d = IA32Register("r10d", 10, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r11d = IA32Register("r11d", 11, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r12d = IA32Register("r12d", 12, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r13d = IA32Register("r13d", 13, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r14d = IA32Register("r14d", 14, IA32RegType.GENERAL_PURPOSE, bit_size=32)
        self.r15d = IA32Register("r15d", 15, IA32RegType.GENERAL_PURPOSE, bit_size=32)

        self.rax = IA32Register("rax", 0, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rcx = IA32Register("rcx", 1, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rdx = IA32Register("rdx", 2, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rbx = IA32Register("rbx", 3, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rsp = IA32Register("rsp", 4, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rbp = IA32Register("rbp", 5, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rsi = IA32Register("rsi", 6, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.rdi = IA32Register("rdi", 7, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r8 = IA32Register("r8", 8, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r9 = IA32Register("r9", 9, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r10 = IA32Register("r10", 10, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r11 = IA32Register("r11", 11, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r12 = IA32Register("r12", 12, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r13 = IA32Register("r13", 13, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r14 = IA32Register("r14", 14, IA32RegType.GENERAL_PURPOSE, bit_size=64)
        self.r15 = IA32Register("r15", 15, IA32RegType.GENERAL_PURPOSE, bit_size=64)

        self.cs = IA32Register("cs", 0, IA32RegType.SEGMENT, bit_size=16)
        self.ss = IA32Register("ss", 1, IA32RegType.SEGMENT, bit_size=16)
        self.ds = IA32Register("ds", 2, IA32RegType.SEGMENT, bit_size=16)
        self.es = IA32Register("es", 3, IA32RegType.SEGMENT, bit_size=16)
        self.fs = IA32Register("fs", 4, IA32RegType.SEGMENT, bit_size=16)
        self.gs = IA32Register("gs", 5, IA32RegType.SEGMENT, bit_size=16)
