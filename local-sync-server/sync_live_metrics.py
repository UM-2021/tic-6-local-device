import requests
from requests.exceptions import ConnectionError
from retry import retry

from decorators import retry_http_5xx
from util import validate_response_json
from exceptions import ExpectedBadResponseException
from constants import ACCESS_TOKEN, ROOM_ID


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
    'type': 'object',
    'properties': {
        'status': {
            'type': 'string'
        },
        'data': {
            'type': 'object'
        }
    },
    'required': ['status', 'data']
}

EXPECTED_BAD_RESPONSE_BACKEND = {
    'type': 'object',
    'properties': {
        'status': {
            'type': 'string'
        },
        'message': {
            'type': 'string'
        }
    },
    'required': ['status', 'message']
}


def _validate_response(response):
    if response.status_code == 404:
        validation_response = validate_response_json(response, EXPECTED_BAD_RESPONSE_SERVER)
        raise ExpectedBadResponseException(f'Detail: {validation_response["detail"]}', response=response)
    response.raise_for_status()
    return validate_response_json(response, EXPECTED_SCHEMA_SERVER)


def _validate_backend_response(response):
    if response.status_code >= 400:
        validation_response = validate_response_json(response, EXPECTED_BAD_RESPONSE_BACKEND)
        raise ExpectedBadResponseException(f'Detail: {validation_response["message"]}', response=response)
    response.raise_for_status()
    return validate_response_json(response, EXPECTED_SCHEMA_BACKEND)


@retry(exceptions=ConnectionError, tries=5, delay=3, jitter=(-2, 2), backoff=1.5)
@retry_http_5xx()
def _get(url):
    response = requests.get(url)
    return _validate_response(response)


@retry(exceptions=ConnectionError, tries=5, delay=3, jitter=(-2, 2), backoff=1.5)
@retry_http_5xx()
def _post(report):
    url = 'https://aggdetector.herokuapp.com/api/liveReports/'
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN
    }
    response = requests.post(url, json=report, headers=headers)
    import curlify
    print(curlify.to_curl(response.request))
    print(response.json())
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
    report = {
        'room': ROOM_ID,
        "averageOccupancy": response.get('average_occupancy'),
        "maxOccupancy": response.get('max_occupancy'),
        "occupancy_threshold": response.get('occupancy_threshold')
    }
    response2 = _post(report)
    print(response2)
