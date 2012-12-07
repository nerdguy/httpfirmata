#!/usr/bin/env python
import cherrypy
from httpfirmata.server import conf, root

cherrypy.quickstart(root, '/', conf)
