[![Build Status](https://github.com/csernazs/pytest-httpserver/workflows/build/badge.svg?branch=master)](https://github.com/csernazs/pytest-httpserver/actions?query=workflow%3Abuild+branch%3Amaster)
[![Documentation Status](https://readthedocs.org/projects/pytest-httpserver/badge/?version=latest)](https://pytest-httpserver.readthedocs.io/en/latest/?badge=latest)
 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=K6PU3AGBZW4QC&item_name=pytest-httpserver&currency_code=EUR&source=url)
[![codecov](https://codecov.io/gh/csernazs/pytest-httpserver/branch/master/graph/badge.svg?token=MX2JXbHqRH)](https://codecov.io/gh/csernazs/pytest-httpserver)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## pytest_httpserver

HTTP server for pytest


### Nutshell

This library is designed to help to test http clients without contacting the real http server.
In other words, it is a fake http server which is accessible via localhost can be started with
the pre-defined expected http requests and their responses.

### Example

#### Handling a simple GET request
```python
def test_my_client(
    httpserver,
):  # httpserver is a pytest fixture which starts the server
    # set up the server to serve /foobar with the json
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    # check that the request is served
    assert requests.get(httpserver.url_for("/foobar")).json() == {"foo": "bar"}
```

#### Handing a POST request with an expected json body
```python
def test_json_request(
    httpserver,
):  # httpserver is a pytest fixture which starts the server
    # set up the server to serve /foobar with the json
    httpserver.expect_request(
        "/foobar", method="POST", json={"id": 12, "name": "foo"}
    ).respond_with_json({"foo": "bar"})
    # check that the request is served
    assert requests.post(
        httpserver.url_for("/foobar"), json={"id": 12, "name": "foo"}
    ).json() == {"foo": "bar"}
```


You can also use the library without pytest. There's a with statement to ensure that the server is stopped.


```python
with HTTPServer() as httpserver:
    # set up the server to serve /foobar with the json
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    # check that the request is served
    print(requests.get(httpserver.url_for("/foobar")).json())
```

### Documentation

Please find the API documentation at https://pytest-httpserver.readthedocs.io/en/latest/.

### Features

You can set up a dozen of expectations for the requests, and also what response should be sent by the server to the client.


#### Requests

There are three different types:

- **permanent**: this will be always served when there's match for this request, you can make as many HTTP requests as you want
- **oneshot**: this will be served only once when there's a match for this request, you can only make 1 HTTP request
- **ordered**: same as oneshot but the order must be strictly matched to the order of setting up

You can also fine-tune the expected request. The following can be specified:

- URI (this is a must)
- HTTP method
- headers
- query string
- data (HTTP body of the request)
- JSON (HTTP body loaded as JSON)


#### Responses

Once you have the expectations for the request set up, you should also define the response you want to send back.
The following is supported currently:

- respond arbitrary data (string or bytearray)
- respond a json (a python dict converted in-place to json)
- respond a Response object of werkzeug
- use your own function

Similar to requests, you can fine-tune what response you want to send:

- HTTP status
- headers
- data


#### Behave support

Using the `BlockingHTTPServer` class, the assertion for a request and the
response can be performed in real order. For more info, see the
[test](tests/test_blocking_httpserver.py), the
[howto](https://pytest-httpserver.readthedocs.io/en/latest/howto.html#running-httpserver-in-blocking-mode)
and the [API
documentation](https://pytest-httpserver.readthedocs.io/en/latest/api.html#blockinghttpserver).


### Missing features
* HTTP/2
* Keepalive
* ~~TLS~~

### Donation

If you want to donate to this project, you can find the donate button at the top
of the README.

Currently, this project is based heavily on werkzeug. Werkzeug does all the heavy lifting
behind the scenes, parsing HTTP request and defining Request and Response objects, which
are currently transparent in the API.

If you wish to donate, please consider donating to them: https://palletsprojects.com/donate
