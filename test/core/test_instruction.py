from flopz.arch.instruction import ArbitraryBytesInstruction


def test_arbitrary_bytes_instruction():
    ai = ArbitraryBytesInstruction(bytes=b'\x11\x99\xaa')
    assert(ai.bytes() == b'\x11\x99\xaa')
    assert(ai.size_bytes() == 3)
    assert(ai.size_bits() == 24)
