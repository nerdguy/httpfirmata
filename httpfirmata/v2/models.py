from __future__ import absolute_import

import json
import traceback

from pyfirmata import Board as FirmataBoard
from pyfirmata import BOARDS
from .exception import InvalidPinException, InvalidConfigurationException
from .storage import boards
from .serializer import ModelsEncoder
from .utils import cached_property
from . import API_VERSION


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

DEFAULT_LAYOUT = BOARDS['arduino']


class Pin(SerializableModel):
    number = None
    type = None
    mode = None
    board_pk = None

    json_export = ('number', 'type', 'mode', 'board_pk', 'value', 'url')

    def __init__(self, board_pk, number, type, *args, **kwargs):
        self.board_pk = board_pk
        self.number = number
        self.type = type
        super(Pin, self).__init__(*args, **kwargs)

    @property
    def identifier(self):
        return '%s%d' % (PIN_TYPES[self.type], self.number)

    @property
    def url(self):
        return "/%s/boards/%s/%s/%d/" % (API_VERSION, self.board_pk, self.type, self.number)

    @property
    def firmata_identifier(self):
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
            self.board.release_pin(self.firmata_identifier)

    def setup(self, mode=None):
        if self.type == 'analog' and mode == 'pwm':
            raise InvalidConfigurationException

        if mode is not None:
            self.mode = mode

    def read(self):
        if self.mode == 'output':
            return None
        pin = self.board.firmata_pin(self.firmata_identifier)
        if pin is not None:
            return pin.read()
        return None

    def write(self, value):
        pin = self.board.firmata_pin(self.firmata_identifier)
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
            pin = self.board.firmata_pin(self.firmata_identifier)
            return pin.value
        return None


class Board(SerializableModel):
    pk = None
    port = None
    pins = None
    name = None
    written_pins = set()

    json_export = ('pk', 'port', 'pins', 'url')

    def __init__(self, pk, port, layout=DEFAULT_LAYOUT, *args, **kwargs):
        self.pk = pk
        self.port = port
        self._board = FirmataBoard(self.port, layout)
        self.pins = {
            'analog': dict(((pin.pin_number, Pin(pk, pin.pin_number, type='analog')) for pin in self._board.analog)),
            'digital': dict(((pin.pin_number, Pin(pk, pin.pin_number, type='digital')) for pin in self._board.digital))
        }

        [setattr(self, k, v) for k, v in kwargs.items()]
        super(Board, self).__init__(*args, **kwargs)

    def __del__(self):
        try:
            self.disconnect()
        except:
            print(traceback.format_exc())

    @property
    def url(self):
        return "/%s/boards/%s/" % (API_VERSION, self.pk)

    def disconnect(self):
        for pin in self.written_pins:
            pin.write(0)
        return self._board.exit()

    def get_pin(self, identifier):
        a_d = identifier[0] == 'a' and 'analog' or 'digital'
        pin_nr = int(identifier[1:])
        return self.pins[a_d][pin_nr]

    def firmata_pin(self, firmata_identifier):
        return self._board.get_pin(firmata_identifier)

    def release_pin(self, firmata_identifier):
        bits = firmata_identifier.split(':')
        a_d = bits[0] == 'a' and 'analog' or 'digital'
        pin_nr = int(bits[1])
        self._board.taken[a_d][pin_nr] = False
