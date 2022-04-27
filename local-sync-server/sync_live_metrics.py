import requests
from requests.exceptions import ConnectionError
from retry import retry

from decorators import retry_http_5xx
from util import validate_response_json
from exceptions import ExpectedBadResponseException

EXPECTED_SCHEMA_SERVER = {
    'type': 'object',
    'properties': {
        'time': {
            'type': 'string'
        },
        'trend': {
            'type': 'number'
        },
        'average_occupancy': {
            'type': 'integer'
        },
        'max_occupancy': {
            'type': 'integer'
        },
        'occupancy_threshold': {
            'type': 'integer'
        },
        'violations': {
            'type': 'integer'
        }
    },
    'required': ['time', 'trend', 'average_occupancy', 'max_occupancy', 'occupancy_threshold', 'violations']
}

EXPECTED_BAD_RESPONSE_SERVER = {
    'type': 'object',
    'properties': {
        'detail': {
            'type': 'string'
        }
    },
    'required': ['detail']
}

EXPECTED_SCHEMA_BACKEND = {
    # TODO: depends on Juanma
    'type': 'object',
    'properties': {
        'time': {
            'type': 'string'
        }
    }
}
EXPECTED_BAD_RESPONSE_BACKEND = {
    # TODO: depends on Juanma
    'type': 'object',
    'properties': {
        'detail': {
            'type': 'string'
        }
    },
    'required': ['detail']
}


def _validate_response(response):
    if response.status_code == 404:
        validation_response = validate_response_json(response, EXPECTED_BAD_RESPONSE_SERVER)
        raise ExpectedBadResponseException(f'Detail: {validation_response["detail"]}', response=response)
    response.raise_for_status()
    return validate_response_json(response, EXPECTED_SCHEMA_SERVER)


def _validate_backend_response(response):
    """
    TODO: depends on Juanma
    if response.status_code == 404:
        validation_response = validate_response_json(response, EXPECTED_BAD_RESPONSE_BACKEND)
        raise Something(f'Detail: {validation_response["detail"]}', response=response)
    response.raise_for_status()
    return validate_response_json(response, EXPECTED_SCHEMA_BACKEND)
    """
    pass


@retry(exceptions=ConnectionError, tries=5, delay=3, jitter=(-2, 2), backoff=1.5)
@retry_http_5xx()
def _get(url):
    response = requests.get(url)
    return _validate_response(response)


@retry(exceptions=ConnectionError, tries=5, delay=3, jitter=(-2, 2), backoff=1.5)
@retry_http_5xx()
def _post(report):
    url = 'URL JUANMA'
    headers = {}
    response = requests.post(url, data=report, headers=headers)
    return _validate_backend_response(response)


if __name__ == '__main__':
    """ TODO: this will get metrics from an area that will represent all cameras. If we want to send information from a
    specific camera, we must hit the /cameras endpoint.
    
    To test a bad area example: ?areas=4564
    To test a 500 status code error: http://httpstat.us/500
    To test the server stopped: kill the server
    To test a bad schema response: modify the schema
    """
    live_url = 'http://localhost:8300/metrics/areas/occupancy/live'
    response = _get(live_url)
    print(response)
    # _post(response)
