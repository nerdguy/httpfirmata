import json


class InvalidPinException(Exception):
    pass


class InvalidConfigurationException(Exception):
    pass


def json_error(message):
        return json.dumps({'error': message})
