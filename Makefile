.PHONY: install test run help

help:
	@echo "Usage:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run unit tests"
	@echo "  make run      - Run the radio system"

install:
	pip install -r requirements.txt

test:
	python3 -m unittest discover tests

run:
	python main.py
