# HTTPFirmata

A [CherryPy](http://www.cherrypy.org) server with an API that talks Firmata to Arduino.

This is not intended to be used in production or anywhere publicly accessible. 

Requires [PyFirmata](https://bitbucket.org/tino/pyfirmata/src/).

## Usage

Run `httpfirmata_run.py` from the `bin` directory.

## Endpoints

* `/ports/`

    * `GET`: returns a list of potential ports for the Arduino.

        `curl http://localhost:8000/ports/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 82
            Server: CherryPy/3.2.2
            Allow: GET, OPTIONS
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, OPTIONS
            Access-Control-Allow-Headers: Content-Type
            Content-Type: application/json
            Connection: close

            [
                "/dev/cu.Bluetooth-PDA-Sync",
                "/dev/cu.Bluetooth-Modem",
                "/dev/cu.usbmodemfd131"
            ]

* `/boards/`

    * `PUT`: Connect a board

        `curl -x PUT http://localhost:8000/boards/ -H 'Content-Type: application/json' --data '{"port": "/dev/cu.usbmodemfd131"}'`

        response:

            HTTP/1.1 201 Created
            Content-Length: 1102
            Content-Type: application/json
            Allow: GET, PUT
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, PUT
            Access-Control-Allow-Headers: Content-Type
            Server: CherryPy/3.2.2
            Connection: close

            {
                "pins": {
                    "analog": {
                        "5": {
                            "board_pk": "1",
                            "type": "analog",
                            "number": 5,
                            "value": null,
                            "mode": null
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "analog",
                            "number": 0,
                            "value": null,
                            "mode": null
                        }
                    },
                    "digital": {
                        "13": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 13,
                            "value": null,
                            "mode": null
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 0,
                            "value": null,
                            "mode": null
                        }
                    }
                },
                "pk": "1",
                "port": "/dev/cu.usbmodemfd131"
            }
    * `GET`: List all connected boards

        `curl http://localhost:8000/boards/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 1104
            Server: CherryPy/3.2.2
            Allow: GET, PUT
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, PUT
            Access-Control-Allow-Headers: Content-Type
            Content-Type: application/json
            Connection: close

            [
                {
                    "pins": {
                        "analog": {
                            "5": {
                                "board_pk": "1",
                                "type": "analog",
                                "number": 5,
                                "value": null,
                                "mode": null
                            },
                            [..snip..]
                            "0": {
                                "board_pk": "1",
                                "type": "analog",
                                "number": 0,
                                "value": null,
                                "mode": null
                            }
                        },
                        "digital": {
                            "13": {
                                "board_pk": "1",
                                "type": "digital",
                                "number": 13,
                                "value": null,
                                "mode": null
                            },
                            [..snip..]
                            "0": {
                                "board_pk": "1",
                                "type": "digital",
                                "number": 0,
                                "value": null,
                                "mode": null
                            }
                        }
                    },
                    "pk": "1",
                    "port": "/dev/cu.usbmodemfd131"
                }
            ]

* `/boards/<board_id>/`

    * `GET`: Retrieves informations about the board's pins.

        `curl http://localhost:8000/boards/1/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 1102
            Server: CherryPy/3.2.2
            Allow: GET, DELETE
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, DELETE
            Access-Control-Allow-Headers: Content-Type
            Content-Type: application/json
            Connection: close

            {
                "pins": {
                    "analog": {
                        "5": {
                            "board_pk": "1",
                            "type": "analog",
                            "number": 5,
                            "value": null,
                            "mode": null,
                            "idnetifier": "a5"
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "analog",
                            "number": 0,
                            "value": null,
                            "mode": null,
                            "identifier": "a0"
                        }
                    },
                    "digital": {
                        "13": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 13,
                            "value": null,
                            "mode": null,
                            "identifier": "d13"
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 0,
                            "value": null,
                            "mode": null,
                            "identifier": "d0"
                        }
                    }
                },
                "pk": "1",
                "port": "/dev/cu.usbmodemfd131"
            }

    * `DELETE`: disconnects the board, resets its pins and removes it from the board list.

        `curl -x DELETE http://localhost:8000/boards/1/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 107
            Server: CherryPy/3.2.2
            Allow: GET, DELETE
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, DELETE
            Access-Control-Allow-Headers: Content-Type
            Content-Type: application/json
            Connection: close

* `/boards/<board_id>/<pin_identifier>/`

    * `POST`: write to the pin

        `curl -x POST http://localhost:8000/boards/1/d13/ -H 'Content-Type: application/json' --data '{"mode": "output", "value": 1}'`

        response:

            HTTP/1.1 200 OK
            Content-Length: 107
            Server: CherryPy/3.2.2
            Allow: GET, POST
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, POST
            Access-Control-Allow-Headers: Content-Type
            Content-Type: application/json
            Connection: close

            {
                "board_pk": "1",
                "type": "digital",
                "number": 13,
                "value": 1.0,
                "mode": "output",
                "identifier": "d13"
            }

    * `GET`: read the pin's value

        `curl http://localhost:8000/boards/1/d13/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 78
            Server: CherryPy/3.2.2
            Allow: GET, POST
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, POST
            Access-Control-Allow-Headers: Content-Type
            Content-Type: application/json
            Connection: close

            {
                "board_pk": "1",
                "type": "digital",
                "number": 13,
                "value": 1.0,
                "mode": "output",
                "identifier": "d13"
            }

## License

MIT License

## Status

This software should be considered alpha.
