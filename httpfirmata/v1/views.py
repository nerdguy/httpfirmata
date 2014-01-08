from __future__ import absolute_import

import glob
import json

from flask import make_response, request

from flask.views import MethodView

from . import API_VERSION
from .exception import InvalidConfigurationException, ObjectNotFoundException, InvalidRequestException, json_error
from .models import Board
from .serializer import ModelsEncoder
from .storage import boards

from serial.serialutil import SerialException


class GenericAPIView(MethodView):
    methods = ('GET', 'OPTIONS')

    def _set_headers(self, response):
        response.headers['X-API-Version'] = API_VERSION

        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Allow'] = ', '.join(self.methods)
        response.headers['Access-Control-Allow-Methods'] = ', '.join(self.methods)
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Content-Type'] = 'application/json'

        return response

    def _error(self, message, status_code=400):
        response = make_response(json_error(message), status_code)
        return response

    def _payload(self):
        content_type = request.headers.get('Content-Type')
        if content_type == 'application/json':
            return json.loads(request.data)
        if content_type == 'application/x-www-form-urlencoded':
            return request.form.to_dict()
        raise InvalidRequestException("Content-Type header can only be 'application/json' or 'application/x-www-form-urlencoded'")

    def dispatch_request(self, *args, **kwargs):
        try:
            response = super(GenericAPIView, self).dispatch_request(*args, **kwargs)
        except ObjectNotFoundException as e:
            return self._error(e.message, status_code=404)
        except InvalidRequestException as e:
            return self._error(e.message, status_code=400)
        else:
            self._set_headers(response)
            return response

    def options(self):
        return make_response(', '.join(self.methods))


class PortListAPI(GenericAPIView):
    def get(self):
        ports = glob.glob('/dev/cu.*')
        resp = make_response(json.dumps(ports))
        return resp


class BoardListAPI(GenericAPIView):
    methods = ('GET', 'PUT', 'OPTIONS')

    def get(self):
        return make_response(json.dumps(boards.values(), cls=ModelsEncoder))

    def put(self):
        board_pk = len(boards) + 1
        data = self._payload()

        try:
            board = Board(pk=board_pk, **data)
        except SerialException:
            raise InvalidRequestException("Port not valid.")

        boards[board_pk] = board
        resp = make_response(board.to_json(), 201)
        return resp


class BoardBaseAPI(GenericAPIView):
    def _get_board(self, board_pk):
        if board_pk in boards:
            return boards[board_pk]
        raise ObjectNotFoundException("Board not found")


class BoardDetailAPI(BoardBaseAPI):
    methods = ('GET', 'DELETE', 'OPTIONS')

    def get(self, board_pk):
        board = self._get_board(board_pk)

        resp = make_response(board.to_json())

        return resp

    def delete(self, board_pk):
        board = self._get_board(board_pk)
        board.disconnect()
        boards.pop(board.pk)
        return make_response('', 204)


class PinDetailAPI(BoardBaseAPI):
    methods = ('GET', 'POST', 'OPTIONS')

    def get(self, board_pk, pin_number):
        board = self._get_board(board_pk)
        return make_response(board.pins[pin_number].to_json())

    def post(self, board_pk, pin_number):
        # set the pin
        data = self._payload()
        value = float(data['value'])
        mode = data.get('mode')
        type = data.get('type')

        board = self._get_board(board_pk)
        try:
            pin = board.pins[pin_number]
        except KeyError:
            raise ObjectNotFoundException("Pin not found")

        try:
            pin.setup(mode=mode, type=type)
        except InvalidConfigurationException:
            raise InvalidRequestException("Pin can\'t be analog AND pwm at the same time.")
        else:
            pin.write(value)
            return make_response(pin.to_json())
