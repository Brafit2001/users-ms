from http import HTTPStatus


class EmptyDbException(Exception):
    """Exception raised when an API returns an empty.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.NO_CONTENT


class NotFoundException(Exception):
    """Exception raised when an API returns an empty.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.NOT_FOUND


class NotAuthorized(Exception):
    """Exception raised when user is not authorized to.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.UNAUTHORIZED


class BadCsvFormatException(Exception):
    """Exception raised when user is not authorized to.

        Attributes:
            message -- explanation of the error
            error_code -- code of the error
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.error_code = HTTPStatus.UNPROCESSABLE_ENTITY
