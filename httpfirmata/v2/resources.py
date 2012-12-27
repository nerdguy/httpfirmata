import cherrypy
import json
import glob

from serial.serialutil import SerialException
from serializer import ModelsEncoder
from models import Board, PIN_TYPES
from storage import boards
from exception import InvalidConfigurationException, json_error
from cherrypy import _cperror
from . import API_VERSION


def error_page_404(status, message, traceback, version):
    return message
cherrypy.config.update({'error_page.404': error_page_404})


def error_page_400(status, message, traceback, version):
    return message
cherrypy.config.update({'error_page.400': error_page_404})


class PortResource(object):
    exposed = True

    def _set_headers(self):
        cherrypy.response.headers['X-API-Version'] = API_VERSION

        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Allow'] = 'GET, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        cherrypy.response.headers['Content-Type'] = 'application/json'

    def OPTIONS(self, *args, **kwargs):
        self._set_headers()
        return cherrypy.response.headers['Allow']

    def GET(self, *args, **kwargs):
        self._set_headers()
        ports = glob.glob('/dev/cu.*')
        return json.dumps(ports)


class BoardResource(object):
    exposed = True

    def _get_board(self, board_pk):
        if board_pk in boards:
            return boards[board_pk]
        raise _cperror.HTTPError(404, json_error("Board not found"))

    def _set_headers(self, board_pk=None, pin_number=None):
        cherrypy.response.headers['X-API-Version'] = API_VERSION

        options = ['GET', 'PUT']
        if board_pk is not None:
            options = ['GET', 'DELETE']
        if pin_number is not None:
            options = ['GET', 'POST']
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = ', '.join(options)
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        cherrypy.response.headers['Allow'] = ', '.join(options)
        cherrypy.response.headers['Content-Type'] = 'application/json'

    def _payload(self, *args, **kwargs):
        content_type = cherrypy.request.headers.get('Content-Type')
        if content_type == 'application/json':
            return json.loads(cherrypy.request.body.read())
        if content_type == 'application/x-www-form-urlencoded':
            return kwargs
        cherrypy.response.status = 400
        raise _cperror.HTTPError(400, json_error("Content-Type header can only be 'application/json' or 'application/x-www-form-urlencoded'"))

    def _check_pin_type(self, pin_type):
        if pin_type not in PIN_TYPES:
            cherrypy.response.status = 400
            raise _cperror.HTTPError(400, json_error("Invalid pin type."))

    @cherrypy.popargs('board_pk', 'pin_type', 'pin_number')
    def OPTIONS(self, board_pk=None, pin_type=None, pin_number=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_number=pin_number)
        self._check_pin_type(pin_type)
        return cherrypy.response.headers['Allow']

    @cherrypy.popargs('board_pk', 'pin_type', 'pin_number')
    def GET(self, board_pk=None, pin_type=None, pin_number=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_number=pin_number)

        if board_pk is None:
            return json.dumps(boards.values(), cls=ModelsEncoder)

        board = self._get_board(board_pk)
        if pin_number is not None:
            self._check_pin_type(pin_type)
            return board.pins[pin_type][pin_number].to_json()
        return board.to_json()

    def PUT(self, *args, **kwargs):
        self._set_headers()
        board_pk = str(len(boards) + 1)
        data = self._payload(*args, **kwargs)

        try:
            board = Board(pk=board_pk, **data)
        except SerialException:
            raise _cperror.HTTPError(400, json_error("Port not valid."))

        self.content = board
        boards[board_pk] = self.content
        cherrypy.response.status = 201
        return self.content.to_json()

    @cherrypy.popargs('board_pk', 'pin_type', 'pin_number')
    def POST(self, board_pk=None, pin_type=None, pin_number=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_number=pin_number)
        self._check_pin_type(pin_type)

        if board_pk is None or pin_number is None:
            cherrypy.response.status = 400
            raise _cperror.HTTPError(400, json_error("Board and/or Pin need to be specified."))

        # set the pin
        data = self._payload(*args, **kwargs)
        value = float(data['value'])
        mode = data.get('mode')

        board = self._get_board(board_pk)
        pin = board.pins[pin_type][pin_number]
        try:
            pin.setup(mode=mode)
        except InvalidConfigurationException:
            cherrypy.response.status = 400
            raise _cperror.HTTPError(400, json_error("Pin can\'t be analog AND pwm at the same time."))
        else:
            pin.write(value)
            return pin.to_json()

    @cherrypy.popargs('board_pk')
    def DELETE(self, board_pk=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk)

        if board_pk is None:
            cherrypy.response.status = 400
            raise _cperror.HTTPError(400, json_error("Board need to be specified."))
        board = self._get_board(board_pk)
        board.disconnect()
        boards.pop(board.pk)
        cherrypy.response.status = 204
