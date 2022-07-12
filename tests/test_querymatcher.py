from werkzeug.datastructures import MultiDict

from pytest_httpserver.httpserver import BooleanQueryMatcher
from pytest_httpserver.httpserver import MappingQueryMatcher
from pytest_httpserver.httpserver import StringQueryMatcher


def assert_match(qm, query_string):
    values = qm.get_comparing_values(query_string)
    assert values[0] == values[1]


def assert_not_match(qm, query_string):
    values = qm.get_comparing_values(query_string)
    assert values[0] != values[1]


def test_qm_string():
    qm = StringQueryMatcher("k1=v1&k2=v2")
    assert_match(qm, b"k1=v1&k2=v2")
    assert_not_match(qm, b"k2=v2&k1=v1")


def test_qm_bytes():
    qm = StringQueryMatcher(b"k1=v1&k2=v2")
    assert_match(qm, b"k1=v1&k2=v2")
    assert_not_match(qm, b"k2=v2&k1=v1")


def test_qm_boolean():
    qm = BooleanQueryMatcher(True)
    assert_match(qm, b"k1=v1")


def test_qm_mapping_string():
    qm = MappingQueryMatcher({"k1": "v1"})
    assert_match(qm, b"k1=v1")


def test_qm_mapping_unordered():
    qm = MappingQueryMatcher({"k1": "v1", "k2": "v2"})
    assert_match(qm, b"k1=v1&k2=v2")
    assert_match(qm, b"k2=v2&k1=v1")


def test_qm_mapping_first_value():
    qm = MappingQueryMatcher({"k1": "v1"})
    assert_match(qm, b"k1=v1&k1=v2")

    qm = MappingQueryMatcher({"k1": "v2"})
    assert_match(qm, b"k1=v2&k1=v1")


def test_qm_mapping_multiple_values():
    md = MultiDict([("k1", "v1"), ("k1", "v2")])
    qm = MappingQueryMatcher(md)
    assert_match(qm, b"k1=v1&k1=v2")
