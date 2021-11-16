from flopz.arch.riscv.riscv_generic_arch import RiscvGenericArchitecture


class RV32IArch(RiscvGenericArchitecture):
    def __init__(self):
        super().__init__(reg_count=32)