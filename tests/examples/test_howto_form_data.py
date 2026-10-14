import requests


def test_form_data(httpserver):
    httpserver.expect_request("/form", method="POST", data_form={"name": "Jane Doe", "flag": ""}).respond_with_data(
        "ok"
    )
    response = requests.post(httpserver.url_for("/form"), data={"flag": "", "name": "Jane Doe"})
    assert response.text == "ok"
