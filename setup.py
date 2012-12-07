import os
from setuptools import setup

from httpfirmata import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = [
    'cherrypy',
    'pyfirmata'
]

setup(
    name = "HTTPFirmata",
    version = ".".join(map(str, __version__)),
    description = "A CherryPy server with an API that talks Firmata to Arduino",
    long_description = read('README.rst'),
    url = 'https://github.com/nerdguy/httpfirmata',
    license = 'MIT',
    author = 'nerdguy',
    author_email = 'guynerd56@gmail.com',
    packages = ['httpfirmata'],
    include_package_data = False,
    scripts = ['httpfirmata/bin/httpfirmata-run.py'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = requirements,
    tests_require = [],
)
