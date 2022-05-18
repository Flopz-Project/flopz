from flopz.arch.register import *
from typing import Tuple, List, Union
from flopz.arch.ia32.instruction_components import ModRM, SIB, Displacement, IA32Opcode
from flopz.util.integer_representation import representable
import enum


class IA32RegType(enum.IntEnum):
    """
    Enumerating the different register types in ia32 architectures.
    """
    GENERAL_PURPOSE = 0
    SEGMENT = 1
    EFLAGS = 2
    EIP = 3
    FPU = 4
    MMX = 5
    XMM = 6


class ValueDescriptor:
    """
    Descriptor class to access IA32Register values.

    For the IA32 architecture the high halves of the first four registers is possible for 8bit operand instructions.
    These are encoded as the encoding for the lower register value +4.
    This Descriptor handles the increase of the value if the targeted register is high.
    """
    def __get__(self, instance: 'IA32Register', owner=None):
        if instance is None:
            return self
        return instance._val + 4 if instance._is_high else instance._val

    def __set__(self, instance, value):
        instance._val = value


class IA32Register(Register):
    """ Class to represent IA32 registers.

    A little more differentiation options are needed for these registers as some can influence the presence
    of the REX byte. Additionally, a Descriptor is added to access the value.
    """
    val = ValueDescriptor()

    def __init__(self, name: str, val: int, reg_type: IntEnum, bit_size: int, is_high=False):
        self._val = 0
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
        """
        Checks if the register requires a REX byte to be encodeable.

        Some registers require a REX byte to be present in the instruction, even if no flags in the REX byte are set.
        This is needed because they share their encoded value with the high halves of the a, c, d & b registers and the
        presence of the REX byte is used to distinguish between the two cases."""
        return self.name in ['spl', 'bpl', 'sil', 'dil']

    def is_high(self):
        return self._is_high

    def __add__(self, other):
        """ Used to combine multiple registers to AddressExpressions. """
        return AddressExpression(base=self) + other

    def __sub__(self, other):
        """ Used to add a negative displacement to AddressExpressions. """
        return AddressExpression(base=self) - other

    def __mul__(self, other):
        """ Used to create an AddressExpressions from the register and a scaling int. """
        return AddressExpression(index=self, scale=other)


class AddressExpression:
    """Class to represent various arithmetic register combinations.

    Combining registers through addition, subtraction or multiplication will result in an AddressExpression.
    Address Expressions are composed of a base register holding the base address,
    an index register and a scale added to the base address (+ scale * index),
    and a displacement value from the resulting address.
    Index and scale without a base or a base without index and scale are both valid, but one has to be set.
    A displacement is optional.

    Parameters:
        base: The base register.
        index: The index register.
        scale: Scaling factor for the index register content. Can be 1, 2, 4 or 8.
        displacement: Signed offset from the address resulting from the other parameters( [base] + scale * [index]).
    """
    def __init__(self, base: IA32Register = None, index: IA32Register = None,
                 scale: int = None, displacement: int = 0):

        # check scale validity
        if scale is not None and not isinstance(scale, int):
            raise TypeError("AddressExpression scale has to be 1, 2, 4 or 8.")
        if scale is not None and scale not in [1, 2, 4, 8]:
            raise ValueError("AddressExpression scale has to be 1, 2, 4 or 8.")

        # check displacement validity
        if not isinstance(displacement, int):
            raise TypeError("AddressExpression displacement has to be int.")
        if not representable(displacement, 32, signed=True):
            raise ValueError("AddressExpression displacements has to be representable by signed 32-bit integer")

        if index is not None and scale is None or index is None and scale is not None:
            raise TypeError("AddressExpression index and scale must always be both defined or both None.")

        if index is None and base is None:
            raise TypeError("One of AddressExpression base and index has to be defined.")

        self.base = base
        self.index = index
        self.scale = scale
        self.displacement = displacement

    def __add__(self, other):
        """ Used to form the initial Expression or extend it. """
        if isinstance(other, int):
            return AddressExpression(base=self.base, index=self.index, scale=self.scale,
                                     displacement=self.displacement + other)
        elif isinstance(other, IA32Register):
            return AddressExpression(base=self.base, index=other, scale=1, displacement=self.displacement)
        elif isinstance(other, AddressExpression):
            return AddressExpression(base=self.base, index=other.index, scale=other.scale,
                                     displacement=self.displacement)
        else:
            raise TypeError(f"Invalid addend {other} to AddressExpression.")

    def __sub__(self, other):
        """ Used to add negative displacement to the Expression. """
        if isinstance(other, int):
            return AddressExpression(base=self.base, index=self.index, scale=self.scale,
                                     displacement=self.displacement - other)
        else:
            raise TypeError(f"Invalid minuend {other} from AddressExpression.")


class MemoryAddress(AddressExpression):
    """
    Combines a AddressExpression with an operand size.

    To be able to correctly address memory in IA32, not only is an address resulting from an
    AddressExpression necessary. As the instructions need to encode the operand size,
    this information is also required to fully create valid instructions.
    """
    def __init__(self, size: int, addr_expr: AddressExpression):
        super().__init__(addr_expr.base, addr_expr.index, addr_expr.scale, addr_expr.displacement)
        self.bit_size = size

    def get_encoding(self, opcode: IA32Opcode = None) -> Tuple[ModRM, Union[SIB, None], Union[Displacement, None]]:
        """
        Returns the bytes that encode the MemoryAddress.

        Returns the ModRM byte and optionally SIB and displacement bytes to encode the MemoryAddress.
        Also sets the necessary bits in the REX byte belonging to the opcode object if the ModRM or SIB encoding
        requires it.
        """
        if self.index is None:
            # encode base address register in ModRM.rm
            if self.displacement is None:
                modrm = ModRM(mod=0, rm=self.base.val, opcode=opcode)
                return modrm, None, None
            elif representable(self.displacement, 8):
                modrm = ModRM(mod=1, rm=self.base.val, opcode=opcode)
                disp = Displacement(self.displacement, 1)
                return modrm, None, disp
            else:
                modrm = ModRM(mod=2, rm=self.base.val, opcode=opcode)
                disp = Displacement(self.displacement, 4)
                return modrm, None, disp
        else:
            # encode ModRM to signal SIB existence
            if self.displacement == 0:
                modrm = ModRM(mod=0, rm=4, opcode=opcode)
                if self.base is not None:
                    sib = SIB(scale=self.scale, index=self.index.val, base=self.base.val, opcode=opcode)
                else:
                    sib = SIB(scale=self.scale, index=self.index.val, base=5, opcode=opcode)
                return modrm, sib, None
            if representable(self.displacement, 8):
                modrm = ModRM(mod=1, rm=4, opcode=opcode)
                if self.base is not None:
                    sib = SIB(scale=self.scale, index=self.index.val, base=self.base.val, opcode=opcode)
                else:
                    sib = SIB(scale=self.scale, index=self.index.val, base=5, opcode=opcode)
                disp = Displacement(self.displacement, 1)
                return modrm, sib, disp
            else:
                modrm = ModRM(mod=2, rm=4, opcode=opcode)
                if self.base is not None:
                    sib = SIB(scale=self.scale, index=self.index.val, base=self.base.val, opcode=opcode)
                else:
                    sib = SIB(scale=self.scale, index=self.index.val, base=5, opcode=opcode)
                disp = Displacement(self.displacement, 4)
                return modrm, sib, disp

            # TODO encode the edge cases for sp index base or bp base


class MemoryAddressFactory:
    """
    Combines a bitsize and an AddressExpression to form a MemoryAddress.

    Used to add operand sizes to AddressExpressions with nice syntax.
    This class is added to the architecture as an attribute. This will allow to write instructions targeting
    memory addresses with a similar syntax like writing instructions that target the registers themselves."""

    def __call__(self, size: int, regis_expr: Union[IA32Register, AddressExpression]):
        """ Takes the size and the address and returns a MemoryAddress

        Return:
            MemoryAddress
        """
        if size not in [8, 16, 32, 64]:
            raise ValueError("Size needs to be either 8, 16, 32, or 64.")
        if isinstance(regis_expr, IA32Register):
            addr_expr = AddressExpression(base=regis_expr)
            return MemoryAddress(size, addr_expr)
        elif isinstance(regis_expr, AddressExpression):
            return MemoryAddress(size, regis_expr)
        else:
            raise TypeError("regis_expr need to be a single register or a AddressExpression")


