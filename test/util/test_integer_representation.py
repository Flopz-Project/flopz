from flopz.util.integer_representation import representable, build_immediates

def test_build_immediates():
    assert(build_immediates(0xF1C, ["[11|4|9:8|10|6|7|3:1|5]", "[5:3]"]) == [1996, 3])


def test_representable():
    assert(representable(12, 5, signed=False, shift=2))
    assert(representable(-2, 3))

    assert(representable(2, 1) is False)

    assert(representable(13, 5, signed=False, shift=2) is False)


