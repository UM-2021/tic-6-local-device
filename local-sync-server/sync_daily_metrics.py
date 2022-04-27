from datetime import datetime

import requests
from requests.exceptions import ConnectionError
from retry import retry

from decorators import retry_http_5xx
from util import validate_response_json
from exceptions import ExpectedBadResponseException

TODAY = datetime.now().strftime("%Y-%m-%d")

EXPECTED_SCHEMA_SERVER = {
    'type': 'object',
    'properties': {
        'occupancy_threshold': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            "minItems": 1,
            "maxItems": 1
        },
        'average_occupancy': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            "minItems": 1,
            "maxItems": 1
        },
        'max_occupancy': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            "minItems": 1,
            "maxItems": 1
        },
        'dates': {
            'type': 'array',
            'items': {
                'type': 'string'
            },
            "minItems": 1,
            "maxItems": 1
        },
    },
    'required': ['occupancy_threshold', 'average_occupancy', 'max_occupancy', 'dates']
}

EXPECTED_BAD_RESPONSE_400_SERVER = {
    'type': 'object',
    'properties': {
        'detail': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'loc': {
                        'type': 'array',
                        'elements': {
                            'type': 'string'
                        }
                    },
                    'msg': {
                        'type': 'string'
                    },
                    'type': {
                        'type': 'string'
                    }
                },
                'required': ['loc', 'msg', 'type']
            },
            "minItems": 1,
            "maxItems": 1
        },
        'body': {
            'type': 'null'
        }
    },
    'required': ['detail', 'body']

}

EXPECTED_BAD_RESPONSE_404_SERVER = {
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
        validation_response = validate_response_json(response, EXPECTED_BAD_RESPONSE_404_SERVER)
        raise ExpectedBadResponseException(f'Detail: {validation_response["detail"]}', response=response)
    if response.status_code == 400:
        validation_response = validate_response_json(response, EXPECTED_BAD_RESPONSE_400_SERVER)
        if validation_response["detail"][0]["type"] == 'value_error.date':
            raise ExpectedBadResponseException(f'Detail: Invalid date.', response=response)
        else:
            raise ExpectedBadResponseException(f'Detail: Unknown bad response.', response=response)
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
    
    To test a bad date example: ?from_date=OOPS (400 status code error)
    To test a bad date example: ?to_date=OOPS (400 status code error)
    To test a bad area example: ?areas=OOPS (404 status code error)
    To test a 500 status code error: http://httpstat.us/500
    To test the server stopped: kill the server
    To test a bad schema response: modify the schema
    """
    live_url = f'http://localhost:8300/metrics/areas/occupancy/daily?from_date={TODAY}&to_date={TODAY}'
    response = _get(live_url)
    print(response)
    # _post(response)
