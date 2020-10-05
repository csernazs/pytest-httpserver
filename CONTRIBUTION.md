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

* coding style is checked by flake8. You can run `make cs` before proceeding
  with the PR. You can also use `autopep8` to fix the issues which gets executed
  by the `make autoformat` command.

* tests should be written for the new code. If there's a complex logic
  implemented, it should be tested on different valid and invalid inputs and
  scenarios.

* the software is released under the MIT license, which is simple and liberal.
  Due to the size of the project, there are no contribution agreements but you
  are informally advised to accept that license.

* it may be obvious but your code should make the software better, not worse.

## How to start developing

* the development is arranged around a virtualenv which needs to be created by
  the `make dev` command. It will create it in the `.venv` directory.

* you can let your IDE of your choice to use the `.venv/bin/python` interpreter
  so it will know all the dependencies and so on.

* running tests on the localhost can be done by issuing `make quick-test`. It is
  "quick" because it tests the software with only one interpreter. Note that the
  library can be used by many supported interpreters and unless it is absolutely
  required, we don't want to drop support.

## More technical details

* for some bigger changes, release notes needs to be written. This is done by
  the 'reno' tool. If you don't write any notes, no problem, it will be written
  by someone who merges your PR.

* documentation also needs to be written and updated. It means mostly
  docstrings, but if the PR changes the code and the way of working
  conceptually, the main documentation (located in the doc directory) needs to
  be updated and extended. This can be also done by someone else if you don't
  want.
