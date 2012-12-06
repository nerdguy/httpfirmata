# HTTPFirmata

A CherryPy server with an API that talks Firmata to Arduino

This is not intended to be used in production or anywhere publicly accessible. 

## Endpoints

* `/boards/`

    * `PUT`: Connect a board

        `curl -x PUT http://localhost:8000/boards/ --data '{"port": "/dev/cu.usbmodemfd131"}'`

        response:

            HTTP/1.1 201 Created
            Content-Length: 1102
            Content-Type: text/html;charset=utf-8
            Allow: GET, PUT
            Server: CherryPy/3.2.2
            Connection: close

            {
                "pins": {
                    "11": {
                        "board_pk": "1",
                        "type": null,
                        "number": 11,
                        "value": null,
                        "mode": null
                    },
                    [..snip..]
                    "8": {
                        "board_pk": "1",
                        "type": null,
                        "number": 8,
                        "value": null,
                        "mode": null
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
            Content-Type: text/html;charset=utf-8
            Connection: close

            [
                {
                    "pins": {
                        "11": {
                            "board_pk": "1",
                            "type": null,
                            "number": 11,
                            "value": null,
                            "mode": null
                        },
                        [..snip..]
                        "8": {
                            "board_pk": "1",
                            "type": null,
                            "number": 8,
                            "value": null,
                            "mode": null
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
            Content-Type: text/html;charset=utf-8
            Connection: close

            {
                "pins": {
                    "11": {
                        "board_pk": "1",
                        "type": null,
                        "number": 11,
                        "value": null,
                        "mode": null
                    },
                    [..snip..]
                    "8": {
                        "board_pk": "1",
                        "type": null,
                        "number": 8,
                        "value": null,
                        "mode": null
                    }
                },
                "pk": "1",
                "port": "/dev/cu.usbmodemfd131"
            }
    * `DELETE`: remove the board from the board list

        `curl -x DELETE http://localhost:8000/boards/1/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 107
            Server: CherryPy/3.2.2
            Allow: GET, DELETE
            Access-Control-Allow-Origin: *
            Content-Type: text/html;charset=utf-8
            Connection: close

* `/boards/<board_id>/<pin_id>/`

    * `POST`: write to the pin

        `curl -x POST http://localhost:8000/boards/1/13/ --data '{"type": "digital", "mode": "output", "value": 1}'`

        response:

            HTTP/1.1 200 OK
            Content-Length: 107
            Server: CherryPy/3.2.2
            Allow: GET, POST
            Access-Control-Allow-Origin: *
            Content-Type: text/html;charset=utf-8
            Connection: close

            {
                "board_pk": "1",
                "type": "digital",
                "number": 13,
                "value": 1.0,
                "mode": "output"
            }

    * `GET`: read the pin's value

        `curl http://localhost:8000/boards/1/13/`

        response:

            HTTP/1.1 200 OK
            Content-Length: 78
            Server: CherryPy/3.2.2
            Allow: GET, POST
            Access-Control-Allow-Origin: *
            Content-Type: text/html;charset=utf-8
            Connection: close

            {
                "board_pk": "1",
                "type": "digital",
                "number": 3,
                "value": 1.0,
                "mode": "output"
            }

## License

MIT License

## Status

This software should be considered alpha.
