.PHONY: venv update-deps

venv:
	python -m venv venv

update-deps:
	pip freeze > requirements.txt
