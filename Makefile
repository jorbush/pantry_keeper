.PHONY: venv update-deps

venv:
	if [ ! -d "venv" ]; then \
		python -m venv venv; \
	fi
	source venv/bin/activate
	pip install -r requirements.txt

update-deps:
	pip freeze > requirements.txt
