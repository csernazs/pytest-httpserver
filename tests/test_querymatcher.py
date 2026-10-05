import pytest
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
    qm = BooleanQueryMatcher(result=True)
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


@pytest.mark.parametrize("query_string", [b"flag=", b"flag", b"flag=&", b"&flag="])
def test_qm_mapping_empty_value(query_string):
    qm = MappingQueryMatcher({"flag": ""})
    assert_match(qm, query_string)
    assert_not_match(qm, b"")
    assert_not_match(qm, b"flag=value")


@pytest.mark.parametrize("query_string", [b"flag=", b"flag", b"flag=&flag="])
def test_qm_mapping_empty_value_is_not_missing(query_string):
    qm = MappingQueryMatcher({})
    assert_not_match(qm, query_string)
    assert_match(qm, b"")


@pytest.mark.parametrize("query_string", [b"flag=&flag=value", b"flag&flag=value"])
def test_qm_mapping_first_value_is_empty(query_string):
    assert_match(MappingQueryMatcher({"flag": ""}), query_string)
    assert_not_match(MappingQueryMatcher({"flag": "value"}), query_string)
    assert_match(MappingQueryMatcher({"flag": "value"}), b"flag=value&flag=")


@pytest.mark.parametrize("query_string", [b"flag=&flag=value", b"flag&flag=value"])
def test_qm_mapping_multiple_values_include_empty(query_string):
    qm = MappingQueryMatcher(MultiDict([("flag", ""), ("flag", "value")]))
    assert_match(qm, query_string)
    assert_not_match(qm, b"flag=value")
    assert_not_match(qm, b"flag=")


def test_qm_mapping_empty_encoded_name():
    qm = MappingQueryMatcher({"empty name": "", "": "value"})
    assert_match(qm, b"empty%20name=&=value")
    assert_match(qm, b"=value&empty+name=")
    assert_not_match(qm, b"=value")
