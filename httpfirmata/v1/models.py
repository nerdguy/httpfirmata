from __future__ import absolute_import

import json
import traceback

from pyfirmata import Arduino
from .exception import InvalidPinException, InvalidConfigurationException
from .storage import boards
from .serializer import ModelsEncoder
from .utils import cached_property


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

    @cached_property
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
            try:
                pin.write(value)
                self._value = value
                self.board.written_pins.add(self)
            finally:
                self.release()
            return
        raise InvalidPinException

    @property
    def value(self):
        if self.mode == 'pwm':
            return self._value
        if self.active:
            pin = self.board.firmata_pin(self.identifier)
            return pin.value
        return None


class Board(SerializableModel):
    pk = None
    port = None
    pins = None
    name = None
    written_pins = set()

    json_export = ('pk', 'port', 'pins')

    def __init__(self, pk, port, *args, **kwargs):
        self.pk = pk
        self.port = port
        self._board = Arduino(self.port)
        self.pins = dict(((i, Pin(pk, i)) for i in range(14)))

        [setattr(self, k, v) for k, v in kwargs.items()]
        super(Board, self).__init__(*args, **kwargs)

    def __del__(self):
        try:
            self.disconnect()
        except:
            print(traceback.format_exc())

    def disconnect(self):
        for pin in self.written_pins:
            pin.write(0)
        return self._board.exit()

    def firmata_pin(self, identifier):
        return self._board.get_pin(identifier)

    def release_pin(self, identifier):
        bits = identifier.split(':')
        a_d = bits[0] == 'a' and 'analog' or 'digital'
        pin_nr = int(bits[1])
        self._board.taken[a_d][pin_nr] = False
