
.venv/bin/pip:
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel

venv: .venv/bin/pip

dev: venv
	.venv/bin/pip3 install -r requirements-dev.txt
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -e .

cs: venv
	.venv/bin/pylint pytest_httpserver
	.venv/bin/pycodestyle pytest_httpserver

mrproper: clean
	rm -rf dist

clean: cov-clean
	rm -rf .venv cluster.egg-info build .eggs __pycache__ */__pycache__

test:
	.venv/bin/pytest tests -s -vv

test-pdb:
	.venv/bin/pytest tests -s -vv --pdb

cov: cov-clean
	.venv/bin/pytest --cov pytest_httpserver --cov-report=term --cov-report=html --cov-report=xml tests

cov-clean:
	rm -rf htmlcov

doc-html: .venv
	.venv/bin/sphinx-build -M html doc doc/_build $(SPHINXOPTS) $(O)
