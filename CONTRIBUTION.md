# Contribution guide

This document describes how to contribute to pytest-httpserver.

In the case you want to add your own code to the source code, create a pull
request, and it will be reviewed in a few days. Currently all developers working
on this software in their spare time so please be patient.

This software has only one main purpose: to be useful for the developers and the
users, to help them to achieve what they intend to do with this small library.
It was created by a few people who are doing it in their spare time. This piece
of software is provided for free under the MIT license.

There's a section in the documentation explaining the design decisions and the main
concepts about the library. Please read it:
https://pytest-httpserver.readthedocs.io/en/latest/background.html


## Rules

There are a few rules you are kindly asked to accept:

* Coding style is checked by `pre-commit`. You can run `make precommit` before
  proceeding with the PR. To install the pre-commit hooks to your git (so it
  will be run for each commit), run `pre-commit install`.

* Tests should be written for the new code. If there's a complex logic
  implemented, it should be tested on different valid and invalid inputs and
  scenarios.

* The software is released under the MIT license, which is simple and liberal.
  Due to the size of the project, there are no contribution agreements, but you
  are informally advised to accept that license.

* It may be obvious but your code should make the software better, not worse.

## How to start developing

* The development is arranged around a virtualenv which needs to be created by
  the `make dev` command. It will create it in the `.venv` directory.

* You can let your IDE of your choice to use the `.venv/bin/python` interpreter,
  so it will know all the dependencies.

* running tests on the localhost can be done by issuing `make test`. Note that the
  library can be used by many supported interpreters and unless it is absolutely
  required, we don't want to drop support.

* running tests on multiple versions of interpreter locally can be done by
  `tox`. Keep in mind that the CI job uses github actions with caching for
  effective use, and `tox` is provided for the developers only.


## More technical details

* Release notes must be written for significant changes. This is done by
  the `reno` tool. If you don't write any notes, no problem, it will be written
  by someone who merges your PR.

* Documentation also needs to be written and updated. It means mostly
  docstrings, but if the PR changes the code and the way of working
  conceptually, the main documentation (located in the doc directory) needs to
  be updated and extended.

* nix files are provided on a best-effort basis. `tox.nix` can be used to run
  `tox`, `shell.nix` can be used instead of poetry for development. No tests
  have been written for these (yet!), so they may be out of sync occasionally.

* to release a new version, you can use the `scripts/release.py` script to make
  the wheels and sdist, generate the changelog, and tag the commit. This tool
  won't upload the artifacts as they need to be checked manually (by installing
  the wheel to a new venv, for example).
