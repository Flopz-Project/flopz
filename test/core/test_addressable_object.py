from flopz.core.addressable_object import AddressableObject

def test_absolute_addressing():
    obj = AddressableObject(object_addr=0x10000000)
    assert(obj.get_absolute_address() == 0x10000000)


def test_relative_addressing():
    obj = AddressableObject(object_addr=0x10000000)
    assert(obj.get_relative_address(other_addr=0x10000004) == -4)