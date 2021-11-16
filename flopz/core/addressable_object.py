class AddressableObject:
    """
    An addressableObject is anything that can be placed into some sort of memory
    each AddressableObject can be addressed by
    - absolute address
    - relative address
      - relative to some other address
    """

    def __init__(self, object_addr: int):
        self.object_addr = object_addr

    def get_absolute_address(self) -> int:
        return self.object_addr

    def get_relative_address(self, other_addr: int) -> int:
        return self.object_addr - other_addr
