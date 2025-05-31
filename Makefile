.PHONY: venv update-deps start-pk stop-pk restart-pk status-pk

venv:
	python -m venv venv

update-deps:
	pip freeze > requirements.txt

start-pk:
	sudo systemctl start pantry-keeper

stop-pk:
	sudo systemctl stop pantry-keeper

restart-pk:
	sudo systemctl restart pantry-keeper

status-pk:
	sudo systemctl status pantry-keeper

fmt:
	autopep8 --recursive --exclude venv --in-place .
