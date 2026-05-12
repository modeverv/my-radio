.PHONY: install test run help

help:
	@echo "Usage:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run unit tests"
	@echo "  make run      - Run the radio system"

install:
	pip install -r requirements.txt

run:
	python main.py
