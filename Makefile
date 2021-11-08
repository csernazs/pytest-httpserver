
export POETRY_VIRTUALENVS_IN_PROJECT=true
EXTRAS ?= dev

.venv/.st-venv-completed:
	poetry install --verbose --extras $(EXTRAS)
	touch .venv/.st-venv-completed

.PHONY: venv
venv: .venv/.st-venv-completed

.PHONY: dev
dev: venv

.PHONY: cs
cs: venv
	.venv/bin/flake8 pytest_httpserver tests

.PHONY: mypy
mypy: venv
	.venv/bin/mypy

.PHONY: autoformat
autoformat: dev
	.venv/bin/autopep8 --in-place --recursive pytest_httpserver tests

.PHONY: mrproper
mrproper: clean
	rm -rf dist

.PHONY: clean
clean: cov-clean doc-clean
	rm -rf .venv *.egg-info build .eggs __pycache__ */__pycache__ .tox poetry.lock

.PHONY: test
test: venv
	.venv/bin/pytest tests -s -vv
	.venv/bin/pytest tests -s -vv --ssl

.PHONY: test-pdb
test-pdb:
	.venv/bin/pytest tests -s -vv --pdb

.PHONY: cov
cov: cov-clean
	.venv/bin/coverage run -m pytest -vv tests
	.venv/bin/coverage run -a -m pytest -vv tests --ssl
	.venv/bin/coverage xml

.PHONY: cov-clean
cov-clean:
	rm -rf htmlcov coverage.xml .coverage

.PHONY: doc
doc: .venv
	.venv/bin/sphinx-build -M html doc doc/_build $(SPHINXOPTS) $(O)

.PHONY: doc-clean
doc-clean:
	rm -rf doc/_build

.PHONY: changes
changes:
	.venv/bin/reno report --output CHANGES.rst --no-show-source
