export POETRY_VIRTUALENVS_IN_PROJECT=true
EXTRAS ?= develop
SPHINXOPTS ?= -n

# do poetry install only in case if poetry.lock or pyproject.toml where updated and
# we require a rebuilt.
.venv/.st-venv-completed: poetry.lock pyproject.toml
	poetry install --verbose --with $(EXTRAS)
	touch .venv/.st-venv-completed


.PHONY: dev
dev: .venv/.st-venv-completed

.PHONY: precommit
precommit: dev
	poetry run pre-commit run -a

.PHONY: mypy
mypy: dev
	.venv/bin/mypy

.PHONY: mrproper
mrproper: clean
	rm -rf dist

.PHONY: clean
clean: cov-clean doc-clean
	rm -rf .venv *.egg-info build .eggs __pycache__ */__pycache__ .tox

.PHONY: test
test: dev
	.venv/bin/pytest tests -s -vv --release
	.venv/bin/pytest tests -s -vv --ssl

.PHONY: test-pdb
test-pdb:
	.venv/bin/pytest tests -s -vv --pdb

.PHONY: cov
cov: cov-clean
	.venv/bin/coverage run -m pytest -vv tests --release
	.venv/bin/coverage run -a -m pytest -vv tests --ssl
	.venv/bin/coverage xml

.PHONY: cov-clean
cov-clean:
	rm -rf htmlcov coverage.xml .coverage

.PHONY: doc
doc: dev
	.venv/bin/sphinx-build -M html doc doc/_build $(SPHINXOPTS) $(O)

.PHONY: doc-clean
doc-clean:
	rm -rf doc/_build

.PHONY: changes
changes: dev
	.venv/bin/reno report --output CHANGES.rst --no-show-source
	poetry run pre-commit run --files CHANGES.rst || true
	poetry run pre-commit run --files CHANGES.rst
