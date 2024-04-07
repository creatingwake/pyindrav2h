import logging

_LOGGER = logging.getLogger(__name__)

class V2HException(Exception):
    def __init__(self, code=None, *args, **kwargs):
        self.message = ""
        super().__init__(*args, **kwargs)
        if code is not None:
            self.code = code
            if isinstance(code, str):
                self.message = self.code
                return
            if self.code == 401:
                self.message = "UNAUTHORIZED"
            elif self.code == 404:
                self.message = "NOT_FOUND"


class WrongCredentialsException(V2HException):
    """Class of exceptions for incomplete credentials."""
    pass


class TimeoutException(V2HException):
    """Class of exceptions for http timeout."""
    pass
