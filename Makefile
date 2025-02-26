.PHONY: all install clean setup poetry-install poetry-setup

all: poetry-setup install

poetry-install:
	python -m pip install poetry

poetry-setup: poetry-install
	poetry config virtualenvs.in-project true

setup: clean poetry-setup install

install:
	poetry install

clean:
	rm -rf .venv || true
	rm -rf build || true
	rm -rf dist || true
	rm poetry.lock || true
	rm -rf *.egg-info || true
	rm -rf **/__pycache__ || true
	rm -f **/*.pyc || true
