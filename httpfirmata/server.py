import cherrypy
from resources import PortResource, BoardResource


conf = {
    'global': {
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8000,
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    }
}


class Root(object):
    pass

root = Root()
root.ports = PortResource()
root.boards = BoardResource()


cherrypy.quickstart(root, '/', conf)
