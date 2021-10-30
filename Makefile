init:
	cp .env-example .env
	pip install --upgrade pip
	pip install ".[test]"
	pip install -r requirements.txt
test:
	python -m pytest tests
ci:
	make test
	make lint
lint:
	python -m flake8 .
format:
	black .
coverage:
	python -m pytest --cov-report term --cov-report xml --cov=src/masonite/billing tests/
	python -m coveralls
publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg src/masonite_billing.egg-info

