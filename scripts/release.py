#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import Iterable


class UsageError(Exception):
    pass


def parse_version() -> str:
    output = subprocess.check_output(["poetry", "version", "--short"], encoding="utf-8")
    version = output.strip()

    return version


def bump_version(path: Path, prefix_list: Iterable[str], current_version: str, new_version: str):
    prefixes = tuple(prefix_list)
    lines = []
    for line in path.open():
        if line.startswith(prefixes):
            line = line.replace(current_version, new_version)
        lines.append(line)

    path.write_text("".join(lines))


def git(*args):
    return subprocess.check_call(["git"] + list(args))


def make(*args):
    return subprocess.check_call(["make"] + list(args))


def check_changelog():
    old_changelog = Path("CHANGES.rst").read_text()
    make("changes")
    new_changelog = Path("CHANGES.rst").read_text()
    if old_changelog == new_changelog:
        raise UsageError("No new changelog entries")


def check_environment():
    for binary in ("git", "make", "poetry"):
        if not which(binary):
            raise UsageError("No such binary: {}".format(binary))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("new_version", help="Version to release")

    args = parser.parse_args()
    new_version: str = args.new_version

    current_version = parse_version()
    if current_version is None:
        raise UsageError("Unable to parse version")

    print(f"Current version: {current_version}")

    if current_version == new_version:
        raise UsageError("Current version is the same as new version")

    check_changelog()

    bump_version(Path("doc/conf.py"), ["version"], current_version, new_version)
    subprocess.check_call(["poetry", "version", new_version])

    git("add", "pyproject.toml", "doc/conf.py")
    git("commit", "-m", "Version bump to {}".format(new_version))
    git("tag", new_version)
    make("changes")
    git("add", "CHANGES.rst")
    git("commit", "-m", "CHANGES.rst: add release notes for {}".format(new_version))
    git("tag", "-f", new_version)


if __name__ == "__main__":
    try:
        main()
    except UsageError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
