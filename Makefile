.PHONY: help install lock update run lint pylint flake8 docker-build docker-up docker-down clean venv

help:
	@echo "Available targets:"
	@echo "  venv          Create a virtual environment"
	@echo "  install       Install dependencies via Poetry (incl. dev)"
	@echo "  lock          Refresh poetry.lock"
	@echo "  update        Update dependencies within version constraints"
	@echo "  run           Run the bot locally"
	@echo "  lint          Run pylint and flake8"
	@echo "  pylint        Run pylint only"
	@echo "  flake8        Run flake8 only"
	@echo "  docker-build  Build the Docker image"
	@echo "  docker-up     Start the bot with docker compose"
	@echo "  docker-down   Stop docker compose services"
	@echo "  clean         Remove caches and build artifacts"

venv:
	python -m venv .venv

install:
	poetry install --with dev

lock:
	poetry lock

update:
	poetry update

run:
	poetry run python autibot.py

lint: pylint flake8

pylint:
	poetry run pylint --disable=W1203,W0603,W0718,E0401 $$(git ls-files '*.py')

flake8:
	poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	rm -rf .ruff_cache .mypy_cache dist build *.egg-info
