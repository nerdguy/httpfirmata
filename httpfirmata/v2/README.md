# HTTPFirmata

A [CherryPy](http://www.cherrypy.org) server with an API that talks Firmata to Arduino.

This is not intended to be used in production or anywhere publicly accessible. 

Requires [PyFirmata](https://bitbucket.org/tino/pyfirmata/src/).

## Usage

Run `httpfirmata_run.py` from the `bin` directory.

## Endpoints

All parameters to the call can be submitted either as json or form-urlencoded data. The `Content-Type` header is required to specify which serialization is used.

All responses will contain headers for CORS.

* `/v2/ports/`

    * `GET`: returns a list of potential ports for the Arduino.

        `curl http://localhost:8000/v2/ports/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 82
            X-Api-Version: v2
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

* `/v2/boards/`

    * `PUT`: Connect a board

        `curl -x PUT http://localhost:8000/v2/boards/ -H 'Content-Type: application/json' --data '{"port": "/dev/cu.usbmodemfd131"}'`

        response:

            HTTP/1.1 201 Created
            Content-Length: 2483
            X-Api-Version: v2
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
                            "mode": null,
                            "url": "/v2/boards/1/analog/5/"
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "analog",
                            "number": 0,
                            "value": null,
                            "mode": null,
                            "url": "/v2/boards/1/analog/0/"
                        }
                    },
                    "digital": {
                        "13": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 13,
                            "value": null,
                            "mode": null,
                            "url": "/v2/boards/1/digital/13/"
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 0,
                            "value": null,
                            "mode": null,
                            "url": "/v2/boards/1/digital/0/"
                        }
                    }
                },
                "pk": "1",
                "port": "/dev/cu.usbmodemfd131"
            }
    * `GET`: List all connected boards

        `curl http://localhost:8000/v2/v2/boards/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 2485
            X-Api-Version: v2
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
                                "mode": null,
                                "url": "/v2/boards/1/analog/5/"
                            },
                            [..snip..]
                            "0": {
                                "board_pk": "1",
                                "type": "analog",
                                "number": 0,
                                "value": null,
                                "mode": null,
                                "url": "/v2/boards/1/analog/0/"
                            }
                        },
                        "digital": {
                            "13": {
                                "board_pk": "1",
                                "type": "digital",
                                "number": 13,
                                "value": null,
                                "mode": null,
                                "url": "/v2/boards/1/digital/13/"
                            },
                            [..snip..]
                            "0": {
                                "board_pk": "1",
                                "type": "digital",
                                "number": 0,
                                "value": null,
                                "mode": null,
                                "url": "/v2/boards/1/digital/0/"
                            }
                        }
                    },
                    "pk": "1",
                    "port": "/dev/cu.usbmodemfd131",
                    "url": "/v2/boards/1/"
                }
            ]

* `/v2/boards/<board_id>/`

    * `GET`: Retrieves informations about the board's pins.

        `curl http://localhost:8000/v2/boards/1/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 2483
            X-Api-Version: v2
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
                            "url": "/v2/boards/1/analog/5/"
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "analog",
                            "number": 0,
                            "value": null,
                            "mode": null,
                            "url": "/v2/boards/1/analog/0/"
                        }
                    },
                    "digital": {
                        "13": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 13,
                            "value": null,
                            "mode": null,
                            "url": "/v2/boards/1/digital/13/"
                        },
                        [..snip..]
                        "0": {
                            "board_pk": "1",
                            "type": "digital",
                            "number": 0,
                            "value": null,
                            "mode": null,
                            "url": "/v2/boards/1/digital/0/"
                        }
                    }
                },
                "pk": "1",
                "port": "/dev/cu.usbmodemfd131",
                "url": "/v2/boards/1/"
            }

    * `DELETE`: disconnects the board, resets its pins and removes it from the board list.

        `curl -x DELETE http://localhost:8000/v2/boards/1/`

        response:

            HTTP/1.1 204 No Content
            X-Api-Version: v2
            Access-Control-Allow-Headers: Content-Type
            Server: CherryPy/3.2.2
            Allow: GET, DELETE
            Date: Thu, 27 Dec 2012 21:33:52 GMT
            Access-Control-Allow-Origin: *
            Access-Control-Allow-Methods: GET, DELETE
            Content-Type: application/json
            Connection: close

* `/v2/boards/<board_id>/<pin_type>/<pin_identifier>/`

    * `POST`: write to the pin

        `curl -x POST http://localhost:8000/v2/boards/1/digital/13/ -H 'Content-Type: application/json' --data '{"mode": "output", "value": 1}'`

        response:

            HTTP/1.1 200 OK
            Content-Length: 117
            X-Api-Version: v2
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
                "url": "/v2/boards/1/digital/13/"
            }

    * `GET`: read the pin's value

        `curl http://localhost:8000/v2/boards/1/digital/13/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 117
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
                "url": "/v2/boards/1/digital/13/"
            }

## License

MIT License

## Status

This software should be considered alpha.
