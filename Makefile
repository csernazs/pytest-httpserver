
venv:
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel

dev: venv
	.venv/bin/pip3 install -r requirements-dev.txt
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -e .

mrproper: clean
	rm -rf dist

clean: cov-clean
	rm -rf .venv cluster.egg-info build

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
