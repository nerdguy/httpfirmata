import cherrypy
from v1 import resources as resources_v1
from v2 import resources as resources_v2


conf = {
    'global': {
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8000,
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },

}


class Root(object):
    pass


class VersionedAPI(object):
    pass


root = Root()
#root = VersionedAPI()
root.ports = resources_v1.PortResource()
root.boards = resources_v1.BoardResource()

root.v1 = VersionedAPI()
root.v1.ports = resources_v1.PortResource()
root.v1.boards = resources_v1.BoardResource()


root.v2 = VersionedAPI()
root.v2.ports = resources_v2.PortResource()
root.v2.boards = resources_v2.BoardResource()
