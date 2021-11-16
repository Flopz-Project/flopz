import logging
import pytest
import tempfile


class DummyLogger(logging.Logger):
    def __init__(self):
        super()
        self.logged_value = ''

    def log(
            self,
            level: int,
            msg,
            *args,
            exc_info = None,
            stack_info = None,
            stacklevel = None,
            extra = None,
            **kwargs,
    ) -> None:
        self.logged_value = msg


@pytest.fixture
def working_directory():
    dir = tempfile.TemporaryDirectory()
    yield dir.name
    dir.cleanup()