import pytest


def pytest_addoption(parser):
    parser.addoption("--ssl", action="store_true", default=False, help="run ssl tests")
    parser.addoption("--release", action="store_true", default=False, help="run release tests")


def pytest_runtest_setup(item):
    markers = [marker.name for marker in item.iter_markers()]

    if not item.config.getoption("--ssl") and "ssl" in markers:
        pytest.skip()
    if item.config.getoption("--ssl") and "ssl" not in markers:
        pytest.skip()
    if not item.config.getoption("--release") and "release" in markers:
        pytest.skip()
