
def get_int_from_str(number: str) -> int:
    """
    :param number: a string containing an integer, in hex (0x prefix) or decimal format
    :return: parsed integer
    """
    if type(number) == int:
        return number

    return int(number, 16) if '0x' in number else int(number)


def get_bytes_from_hex_str(s: str) -> bytes:
    return bytes.fromhex(s)