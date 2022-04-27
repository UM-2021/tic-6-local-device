from requests import RequestException


class ExpectedBadResponseException(RequestException):

    def __init__(self, *args, **kwargs):
        super(ExpectedBadResponseException, self).__init__(*args, **kwargs)


class RetriableException(Exception):
    """A `Generic Exception` for use `@retry`."""
    pass
