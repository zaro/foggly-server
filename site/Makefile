
env-create:
	mkdir -p env
	virtualenv -p `which python3.5` env/

pip-upgrade:
	pip install --upgrade pip

pip-save:
	pip freeze > requirements.txt

pip-install:
	pip install -r requirements.txt
