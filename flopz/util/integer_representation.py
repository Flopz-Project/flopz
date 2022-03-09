from typing import Union, Tuple, List
import re
from bitstring import BitArray


def representable(val: int, bits: int, signed: bool = True, shift: int = 0) -> bool:
    """
    Checks if the value is representable with the given number of bits

    Will return True if it is possible to encode the value in 'val' with the number of bits given in 'bits'.
    Additionally, it can be specified if a sign has to be encoded or if the value can be rightshifted before encoding.
    If encoding the value is not possible, the function will return False.

    Parameters:
        val (int): The value to be encoded.
        bits (int): The amount of bits available for encoding.
        signed (bool): Does the encoding include a sign or can we encode the unsigned value.
        shift (int): By which amount is the value supposed to be rightshifted before encoding.

    Returns:
        bool: Can the value be encoded with the given bits and parameters.
    """

    if val % (1 << shift) != 0:
        return False
    val >>= shift
    if signed:
        return -2**(bits-1) <= val < 2**(bits-1)
    else:
        return 0 <= val < 2**bits


def build_immediates(val: int, specs: Union[str, List[str]]) -> List[int]:
    """
    Builds immediates for encoding offsets etc in riscv instructions.

    Riscv offsets come with specifications like "offset[11|4|9:8|10|6|7|3:1|5]",
    This method takes the "[11|4|9:8|10|6|7|3:1|5]" part as a spec string and will return the encoded result
    as an integer representation.
    Providing multiple specs is possible (as the offset is often split into multiple immediates).

    Parameters:
        val (int): The value (offset) that is to be encoded in the immediate(s).
        specs (Union[str, List[str]]): The spec strings copied from the official riscv documentation
                                        for the implemented instruction.

    Returns:
        List[int]: A list of the integers representing the offsets immediate encoding(s).
                    These can be given to the instructions operands.
    """

    parsed_specs = list()
    if not isinstance(specs, list):
        specs = [specs]
    valid_rex = re.compile('\[((\d+|\d+:\d+)\|)*(\d+|\d+:\d+)\]')
    for spec in specs:
        if valid_rex.fullmatch(spec) is None:
            raise ValueError(f"Invalid spec {spec}.")
        parts = spec[1:-1].split('|')
        parsed = list()
        for p in parts:
            parsed.append(tuple(int(n) for n in p.split(':')))
        parsed_specs.append(parsed)

    representation_bits = max(max(t) for s in parsed_specs for t in s) + 1

    if val >= 0:
        ba = BitArray(length=representation_bits, uint=val)
    else:
        ba = BitArray(length=representation_bits, int=val)
    ba_len = len(ba)

    results = list()
    for spec in parsed_specs:
        imm = 0
        for i, bits in enumerate(spec):
            if len(bits) == 1:
                imm <<= 1
                imm += ba[ba_len-bits[0]-1]
            elif len(bits) == 2:
                high = bits[0]
                low = bits[1]
                imm <<= high - low + 1
                if not low < high:  # maybe include logic for slices [low:high]
                    raise ValueError(f"Invalid spec {specs[i]}. (Invalid slice {high}:{low})")
                imm += ba[ba_len-high-1:ba_len-low].uint
            else:
                raise ValueError(f"Invalid spec {specs[i]}.")
        results.append(imm)
    return results
