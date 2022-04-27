import jsonschema
import simplejson


def validate_response_json(response, schema=None):
    try:
        json = response.json()
        if not schema:
            return json
        jsonschema.validate(json, schema)
        return json
    except simplejson.JSONDecodeError:
        raise Exception('Expected a JSON response')
    except jsonschema.ValidationError:
        raise Exception('Unexpected JSON schema response')
