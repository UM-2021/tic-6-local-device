from requests import RequestException
from retry import retry

from exceptions import RetriableException

HTTP_500_RETRIES = {'tries': 7, 'delay': 5, 'max_delay': 30, 'backoff': 2, 'jitter': (0, 10)}


def retry_http_5xx(retries=None):
    if retries is None:
        retries = HTTP_500_RETRIES

    def analyze_exception(func):

        def call(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestException as exception:
                if exception.response is None:
                    raise
                status_code = exception.response.status_code
                if 500 <= status_code <= 599:
                    raise RetriableException('Server Error')
                raise
        return call

    def assemble_retries(func):
        return retry(RetriableException, **retries)(analyze_exception(func))

    def no_retries(func):
        return func

    if retries:
        return assemble_retries
    else:
        return no_retries