from flopz.arch.arm.thumb.instructions import encode_to_12b_imm, decode_from_12b_imm
import pytest

def test_immediate_encoding():
    assert(encode_to_12b_imm(8) == 8)

    with pytest.raises(ValueError):
        encode_to_12b_imm(0x1FFFFFFFF)

    assert(encode_to_12b_imm(0x01100000) == 0b011110001000)
    assert(encode_to_12b_imm(0x10000000) == 0b010110000000)

    with pytest.raises(ValueError):
        encode_to_12b_imm(0xAA0F0000)
        encode_to_12b_imm(0x00A1B000)

    assert(decode_from_12b_imm(encode_to_12b_imm(0xAB00AB00)) == 0xAB00AB00)
    assert(decode_from_12b_imm(encode_to_12b_imm(0xFEFEFEFE)) == 0xFEFEFEFE)
    assert(decode_from_12b_imm(encode_to_12b_imm(0x00120012)) == 0x00120012)

    assert(decode_from_12b_imm(0x007) == 7)
