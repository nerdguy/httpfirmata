import json
from datetime import datetime

from pyfirmata import Arduino
from exception import InvalidPinException, InvalidConfigurationException
from storage import boards
from serializer import ModelsEncoder


class SerializableModel(object):
    json_export = ()

    serializer = ModelsEncoder

    def to_json(self):
        return json.dumps(self, cls=self.serializer)


PIN_MODES = {
    'input': 'i',
    'output': 'o',
    'pwm': 'p',
    'servo': 's',
}

PIN_TYPES = {
    'analog': 'a',
    'digital': 'd'
}


class Pin(SerializableModel):
    number = None
    type = None
    mode = None
    board_pk = None

    json_export = ('number', 'type', 'mode', 'board_pk', 'value')

    def __init__(self, board_pk, number, *args, **kwargs):
        self.board_pk = board_pk
        self.number = number
        super(Pin, self).__init__(*args, **kwargs)

    @property
    def identifier(self):
        if self.active:
            return '%s:%d:%s' % (PIN_TYPES[self.type], self.number, PIN_MODES[self.mode])
        raise ValueError

    @property
    def board(self):
        return boards[self.board_pk]

    @property
    def active(self):
        return self.type is not None and self.mode is not None

    def release(self):
        if self.active:
            self.board.release_pin(self.identifier)

    def setup(self, type=None, mode=None):
        if type == 'analog' and mode == 'pwm':
            raise InvalidConfigurationException

        if type is not None:
            self.type = type
        if mode is not None:
            self.mode = mode

    def read(self):
        if self.mode == 'output':
            return None
        pin = self.board.firmata_pin(self.identifier)
        if pin is not None:
            return pin.read()
        return None

    def write(self, value):
        pin = self.board.firmata_pin(self.identifier)
        if pin is not None and self.mode != 'input':
            pin.write(value)
            self.release()
            return
        raise InvalidPinException

    @property
    def value(self):
        if self.active:
            pin = self.board.firmata_pin(self.identifier)
            return pin.value
        return None

    def to_json(self):
        resp = super(Pin, self).to_json()
        self.release()
        return resp


class Board(SerializableModel):
    pk = None
    port = None
    pins = None
    name = None

    json_export = ('pk', 'port', 'pins')

    def __init__(self, pk, port, *args, **kwargs):
        self.pk = pk
        self.port = port
        self._board = Arduino(self.port)
        self.pins = dict(((str(i), Pin(pk, i)) for i in range(14)))

        [setattr(self, k, v) for k, v in kwargs.items()]
        super(Board, self).__init__(*args, **kwargs)

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        return self._board.exit()

    def to_json(self):
        from serializer import ModelsEncoder

        return json.dumps(self, cls=ModelsEncoder)

    def firmata_pin(self, identifier):
        return self._board.get_pin(identifier)

    def release_pin(self, identifier):
        bits = identifier.split(':')
        a_d = bits[0] == 'a' and 'analog' or 'digital'
        pin_nr = int(bits[1])
        self._board.taken[a_d][pin_nr] = False
