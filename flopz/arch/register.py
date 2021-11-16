from enum import IntEnum

import bitstring

"""
notes:
 - assume that we always have all registers as instance
 - provided by arch.*.$arch object
 - then, __call__ can be used to quickly get the encoded version of a register
"""


class Register:
    def __init__(self, name: str, val: int, reg_type: IntEnum):
        self.name = name
        self.type = reg_type
        self.val = val

    def value(self):
        return self.val

    def encode(self) -> bitstring.BitArray:
        """
        :return: this register, encoded to target architecture-specific encoding, as bitArray
        """
        return bitstring.BitArray()

    @staticmethod
    def name():
        # override this
        return ''
