from __future__ import annotations

import urllib.parse

import pytest

parse_qsl_semicolon_cases = [
    ("&", []),
    ("&&", []),
    ("&a=b", [("a", "b")]),
    ("a=a+b&b=b+c", [("a", "a b"), ("b", "b c")]),
    ("a=1&a=2", [("a", "1"), ("a", "2")]),
    ("a=", [("a", "")]),
    ("a=foo bar&b=bar foo", [("a", "foo bar"), ("b", "bar foo")]),
    ("a=foo%20bar&b=bar%20foo", [("a", "foo bar"), ("b", "bar foo")]),
    ("a=%20%21%22%23%24%25%26%27%28%29%2A%2B%2C%2F%3A%3B%3D%3F%40%5B%5D", [("a", " !\"#$%&'()*+,/:;=?@[]")]),
]


@pytest.mark.parametrize(("qs", "expected"), parse_qsl_semicolon_cases)
def test_qsl(qs: str, expected: list[tuple[bytes, bytes]]):
    assert urllib.parse.parse_qsl(qs, keep_blank_values=True) == expected
