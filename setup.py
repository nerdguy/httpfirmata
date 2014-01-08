from __future__ import absolute_import
import os
from setuptools import setup, find_packages

VERSION = "0.0.9"
__version__ = tuple(map(int, VERSION.split('.')))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = [
    'flask',
    "Werkzeug",
    'pyfirmata',
]

setup(
    name="HTTPFirmata",
    version=VERSION,
    description="A CherryPy server with an API that talks Firmata to Arduino",
    long_description=read('README.md'),
    url='https://github.com/nerdguy/httpfirmata',
    license='MIT',
    author='nerdguy',
    author_email='guynerd56@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    scripts=['bin/httpfirmata_run.py'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=requirements,
    tests_require=[],
)
