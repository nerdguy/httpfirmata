import json
from pyfirmata import Arduino


def json_error(message):
        return json.dumps({'error': message})


def json_404():
        return json_error('Not Found.')


class ModelsEncoder(json.JSONEncoder):
    def default(self, obj):
        from models import SerializableModel

        if isinstance(obj, Arduino):
            return

        if isinstance(obj, SerializableModel):
            _dict = dict(((k, getattr(obj, k)) for k in obj.json_export))
            if hasattr(obj, 'release'):
                obj.release()
            return _dict
