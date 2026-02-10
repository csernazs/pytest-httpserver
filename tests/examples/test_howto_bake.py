import requests

from pytest_httpserver import HTTPServer


def test_bake_json_api(httpserver: HTTPServer) -> None:
    # bake common defaults so you don't repeat them for every expect_request
    json_api = httpserver.bake(method="POST", headers={"Content-Type": "application/json"})

    json_api.expect_request("/users").respond_with_json({"id": 1, "name": "Alice"}, status=201)
    json_api.expect_request("/items").respond_with_json({"id": 42, "name": "Widget"}, status=201)

    resp = requests.post(
        httpserver.url_for("/users"),
        json={"name": "Alice"},
    )
    assert resp.status_code == 201
    assert resp.json() == {"id": 1, "name": "Alice"}

    resp = requests.post(
        httpserver.url_for("/items"),
        json={"name": "Widget"},
    )
    assert resp.status_code == 201
    assert resp.json() == {"id": 42, "name": "Widget"}
