from __future__ import absolute_import

from flask import Flask

from .v1 import views as _v1
from .v2 import views as _v2


app = Flask(__name__)

app.add_url_rule('/v2/boards/<int:board_pk>/<pin_type>/<int:pin_number>/', view_func=_v2.PinDetailAPI.as_view('v2:pin_detail'))
app.add_url_rule('/v2/boards/<int:board_pk>/', view_func=_v2.BoardDetailAPI.as_view('v2:board_detail'))
app.add_url_rule('/v2/boards/', view_func=_v2.BoardListAPI.as_view('v2:board_list'))
app.add_url_rule('/v2/ports/', view_func=_v2.PortListAPI.as_view('v2:port_list'))

app.add_url_rule('/v1/boards/<int:board_pk>/<int:pin_number>/', view_func=_v1.PinDetailAPI.as_view('v1:pin_detail'))
app.add_url_rule('/v1/boards/<int:board_pk>/', view_func=_v1.BoardDetailAPI.as_view('v1:board_detail'))
app.add_url_rule('/v1/boards/', view_func=_v1.BoardListAPI.as_view('v1:board_list'))
app.add_url_rule('/v1/ports/', view_func=_v1.PortListAPI.as_view('v1:port_list'))

app.add_url_rule('/boards/<int:board_pk>/<int:pin_number>/', view_func=_v1.PinDetailAPI.as_view('pin_detail'))
app.add_url_rule('/boards/<int:board_pk>/', view_func=_v1.BoardDetailAPI.as_view('board_detail'))
app.add_url_rule('/boards/', view_func=_v1.BoardListAPI.as_view('board_list'))
app.add_url_rule('/ports/', view_func=_v1.PortListAPI.as_view('port_list'))
