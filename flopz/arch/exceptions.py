
class InvalidArgumentException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidArgumentRangeException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidFlagCombinationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class AutoInstructionFailure(Exception):
    def __init__(self, message):
        super().__init__(message)
