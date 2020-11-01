
PYTHON ?= python3

.venv/bin/pip:
	${PYTHON} -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel

.PHONY: venv
venv: .venv/bin/pip

.PHONY: dev
dev: venv
	.venv/bin/pip3 install -e .[dev]

.PHONY: cs
cs: venv
	.venv/bin/flake8 pytest_httpserver tests

.PHONY: autoformat
autoformat: dev
	.venv/bin/autopep8 --in-place --recursive pytest_httpserver tests

.PHONY: mrproper
mrproper: clean
	rm -rf dist

.PHONY: clean
clean: cov-clean doc-clean
	rm -rf .venv *.egg-info build .eggs __pycache__ */__pycache__ .tox

.PHONY: quick-test
quick-test:
	.venv/bin/pytest tests -s -vv

.PHONY: test
test:
	tox

.PHONY: test-pdb
test-pdb:
	.venv/bin/pytest tests -s -vv --pdb

.PHONY: cov
cov: cov-clean
	.venv/bin/coverage run -m pytest -vv tests
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
