import pytest
import requests


def test_connection_refused():
    # assumes that there's no server listening at localhost:1234
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get("http://localhost:1234")
