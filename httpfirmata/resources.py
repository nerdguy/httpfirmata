import cherrypy
import json
import glob

from serial.serialutil import SerialException
from serializer import ModelsEncoder, json_error, json_404
from models import Board
from storage import boards
from exception import InvalidConfigurationException


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
        cherrypy.response.status = 404
        return json_404()

    def _set_headers(self, board_pk=None, pin_number=None):
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
        if cherrypy.request.headers['Content-Type'] == 'application/json':
            return json.loads(cherrypy.request.body.read())
        return kwargs

    @cherrypy.popargs('board_pk', 'pin_number')
    def OPTIONS(self, board_pk=None, pin_number=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_number=pin_number)
        return cherrypy.response.headers['Allow']

    @cherrypy.popargs('board_pk', 'pin_number')
    def GET(self, board_pk=None, pin_number=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_number=pin_number)

        if board_pk is None:
            return json.dumps(boards.values(), cls=ModelsEncoder)

        board = self._get_board(board_pk)
        if pin_number is not None:
            return board.pins[pin_number].to_json()
        return board.to_json()

    def PUT(self, *args, **kwargs):
        self._set_headers()
        board_pk = str(len(boards) + 1)
        data = self._payload(*args, **kwargs)

        try:
            board = Board(pk=board_pk, **data)
        except SerialException:
            cherrypy.response.status = 400
            return json_error("Port not valid.")

        self.content = board
        boards[board_pk] = self.content
        cherrypy.response.status = 201
        return self.content.to_json()

    @cherrypy.popargs('board_pk', 'pin_number')
    def POST(self, board_pk=None, pin_number=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk, pin_number=pin_number)

        if board_pk is None or pin_number is None:
            cherrypy.response.status = 400
            return json_error('Board and/or Pin need to be specified.')
        # set the pin
        data = self._payload(*args, **kwargs)
        value = float(data['value'])
        mode = data.get('mode')
        type = data.get('type')

        board = self._get_board(board_pk)
        pin = board.pins[pin_number]
        try:
            pin.setup(mode=mode, type=type)
        except InvalidConfigurationException:
            cherrypy.response.status = 400
            return json_error('Pin can\'t be analog AND pwm at the same time.')
        else:
            pin.write(value)
            return pin.to_json()

    @cherrypy.popargs('board_pk')
    def DELETE(self, board_pk=None, *args, **kwargs):
        self._set_headers(board_pk=board_pk)

        if board_pk is None:
            cherrypy.response.status = 400
            return json_error('Board need to be specified.')
        board = self._get_board(board_pk)
        boards.pop(board.pk)
        cherrypy.response.status = 204
