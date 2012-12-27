import cherrypy
import json
import glob

from serial.serialutil import SerialException
from serializer import ModelsEncoder
from models import Board
from storage import boards
from exception import InvalidConfigurationException, json_error
from cherrypy import _cperror


def error_page_404(status, message, traceback, version):
    return message
cherrypy.config.update({'error_page.404': error_page_404})


def error_page_400(status, message, traceback, version):
    return message
cherrypy.config.update({'error_page.400': error_page_404})


class Root(object):
    pass


class PortResource(object):
    exposed = True

    def _set_headers(self):
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

    def _set_headers(self, board_pk=None, pin_identifier=None):
        options = ['GET', 'PUT']
        if board_pk is not None:
            options = ['GET', 'DELETE']
        if pin_identifier is not None:
            options = ['GET', 'POST']
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = ', '.join(options)
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        cherrypy.response.headers['Allow'] = ', '.join(options)
        cherrypy.response.headers['Content-Type'] = 'application/json'

    def _payload(self, *args, **kwargs):
        if cherrypy.request.headers['Content-Type'] == 'application/json':
            return json.loads(cherrypy.request.body.read())
        return kwargs

    @cherrypy.popargs('board_pk', 'pin_identifier')
    def OPTIONS(self, board_pk=None, pin_identifier=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_identifier=pin_identifier)
        return cherrypy.response.headers['Allow']

    @cherrypy.popargs('board_pk', 'pin_identifier')
    def GET(self, board_pk=None, pin_identifier=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_identifier=pin_identifier)

        if board_pk is None:
            return json.dumps(boards.values(), cls=ModelsEncoder)

        board = self._get_board(board_pk)
        if pin_identifier is not None:
            return board.get_pin(pin_identifier).to_json()
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

    @cherrypy.popargs('board_pk', 'pin_identifier')
    def POST(self, board_pk=None, pin_identifier=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_identifier=pin_identifier)

        if board_pk is None or pin_identifier is None:
            cherrypy.response.status = 400
            raise _cperror.HTTPError(400, json_error("Board and/or Pin need to be specified."))
        # set the pin
        data = self._payload(*args, **kwargs)
        value = float(data['value'])
        mode = data.get('mode')

        board = self._get_board(board_pk)
        pin = board.get_pin(pin_identifier)
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
