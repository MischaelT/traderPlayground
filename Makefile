SHELL := /bin/bash

test:
	py.test app/tests/test_testStrategy.py

run:
	python3 app/main.py