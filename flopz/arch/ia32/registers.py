from flopz.arch.register import *


class IA32_Register(Register):
    def __init__(self, name: str, val: int, reg_type: IntEnum, bit_size: int, is_high=False):
        super().__init__(name, val, reg_type)
        self.bit_size = bit_size
        self._is_high = is_high

    def __str__(self):
        return f"IA32 Register {self.name} ({self.bit_size}bit)"

    def get_val(self):
        if self._is_high:
            return self.val + 4
        else:
            return self.val

    def requires_rex(self):
        return self.name in ['spl', 'bpl', 'sil', 'dil']

    def is_high(self):
        return self._is_high