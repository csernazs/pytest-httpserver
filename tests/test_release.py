# TODO: skip if poetry is not available or add mark to test it explicitly


import email
import re
import shutil
import subprocess
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from typing import Tuple

import pytest
import toml

pytestmark = pytest.mark.release

NAME = "pytest-httpserver"
NAME_UNDERSCORE = NAME.replace("-", "_")


@pytest.fixture(scope="session")
def pyproject_path() -> Path:
    return Path("pyproject.toml")


@pytest.fixture(scope="session")
def pyproject(pyproject_path: Path):
    assert pyproject_path.is_file()
    with pyproject_path.open() as infile:
        pyproject = toml.load(infile)
    return pyproject


class Wheel:
    def __init__(self, path: Path):
        self.path = path

    @property
    def wheel_out_dir(self) -> Path:
        return self.path.parent.joinpath("wheel")

    def extract(self):
        with zipfile.ZipFile(self.path) as zf:
            zf.extractall(self.wheel_out_dir)

    def get_meta(self, version: str, name: str = NAME_UNDERSCORE) -> email.message.Message:
        metadata_path = self.wheel_out_dir.joinpath(f"{name}-{version}.dist-info", "METADATA")
        with metadata_path.open() as metadata_file:
            msg = email.message_from_file(metadata_file)

        return msg


class Sdist:
    def __init__(self, path: Path):
        self.path = path

    @property
    def sdist_out_dir(self) -> Path:
        return self.path.parent.joinpath("sdist")

    def extract(self):
        with tarfile.open(self.path, mode="r:gz") as tf:
            tf.extractall(self.sdist_out_dir)


@dataclass
class Build:
    wheel: Wheel
    sdist: Sdist

    def extract(self):
        self.wheel.extract()
        self.sdist.extract()


@pytest.fixture(scope="session")
def build(request) -> Iterable[Build]:
    dist_path = Path("dist").resolve()
    if dist_path.is_dir():
        shutil.rmtree(dist_path)

    try:
        subprocess.run(["poetry", "build"], check=True)
        assert dist_path.is_dir()
        wheels = list(dist_path.glob("*.whl"))
        sdists = list(dist_path.glob("*.tar.gz"))
        assert len(wheels) == 1
        assert len(sdists) == 1
        build = Build(wheel=Wheel(wheels[0]), sdist=Sdist(sdists[0]))
        build.extract()
        yield build

    finally:
        shutil.rmtree(dist_path)


@pytest.fixture(scope="session")
def version(pyproject) -> str:
    return pyproject["tool"]["poetry"]["version"]


def version_to_tuple(version: str) -> Tuple:
    return tuple([int(x) for x in version.split(".")])


def test_no_duplicate_classifiers(build: Build, pyproject):
    pyproject_meta = pyproject["tool"]["poetry"]
    wheel_meta = build.wheel.get_meta(version=pyproject_meta["version"])
    classifiers = sorted(wheel_meta.get_all("Classifier"))
    unique_classifiers = sorted(set(wheel_meta.get_all("Classifier")))

    assert classifiers == unique_classifiers


def test_python_version(build: Build, pyproject):
    pyproject_meta = pyproject["tool"]["poetry"]
    wheel_meta = build.wheel.get_meta(version=pyproject_meta["version"])
    python_dependency = pyproject_meta["dependencies"]["python"]
    m = re.match(r">=(\d+\.\d+),<(\d+\.\d+)", python_dependency)
    if m:
        min_version, max_version = m.groups()
    else:
        raise ValueError(python_dependency)

    min_version_tuple = version_to_tuple(min_version)
    max_version_tuple = version_to_tuple(max_version)

    for classifier in wheel_meta.get_all("Classifier"):
        if classifier.startswith("Programming Language :: Python ::"):
            version_tuple = version_to_tuple(classifier.split("::")[-1].strip())
            if len(version_tuple) > 1:
                assert version_tuple >= min_version_tuple and version_tuple < max_version_tuple


def test_wheel_no_extra_contents(build: Build, version: str):
    wheel_dir = build.wheel.wheel_out_dir
    wheel_contents = list(wheel_dir.iterdir())
    assert len(wheel_contents) == 2
    assert wheel_dir.joinpath(NAME_UNDERSCORE).is_dir()
    assert wheel_dir.joinpath(f"{NAME_UNDERSCORE}-{version}.dist-info").is_dir()

    package_contents = {path.name for path in wheel_dir.joinpath(NAME_UNDERSCORE).iterdir()}
    assert package_contents == {
        "__init__.py",
        "blocking_httpserver.py",
        "httpserver.py",
        "py.typed",
        "pytest_plugin.py",
    }


def test_sdist_contents(build: Build, version: str):
    sdist_base = build.sdist.sdist_out_dir.joinpath(f"pytest_httpserver-{version}")

    subdir_contents = {
        ".": {
            "CHANGES.rst",
            "CONTRIBUTION.md",
            "doc",
            "example_pytest.py",
            "example.py",
            "LICENSE",
            "PKG-INFO",
            "pyproject.toml",
            "pytest_httpserver",
            "README.md",
            "setup.py",
            "tests",
        },
        "doc": {
            "_static",
            "api.rst",
            "background.rst",
            "changes.rst",
            "conf.py",
            "fixtures.rst",
            "guide.rst",
            "howto.rst",
            "index.rst",
            "Makefile",
            "tutorial.rst",
            "upgrade.rst",
        },
        "pytest_httpserver": {
            "__init__.py",
            "blocking_httpserver.py",
            "httpserver.py",
            "py.typed",
            "pytest_plugin.py",
        },
        "tests": {
            "assets",
            "conftest.py",
            "test_blocking_httpserver.py",
            "test_blocking_httpserver_howto.py",
            "test_handler_errors.py",
            "test_headers.py",
            "test_json_matcher.py",
            "test_mixed.py",
            "test_oneshot.py",
            "test_ordered.py",
            "test_permanent.py",
            "test_port_changing.py",
            "test_querymatcher.py",
            "test_querystring.py",
            "test_release.py",
            "test_ssl.py",
            "test_urimatch.py",
            "test_wait.py",
            "test_with_statement.py",
        },
    }

    for subdir, subdir_content in subdir_contents.items():
        contents = {path.name for path in sdist_base.joinpath(subdir).iterdir()}
        assert contents == subdir_content


def test_poetry_check():
    subprocess.run(["poetry", "check"], check=True)
