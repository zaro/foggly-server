
env-create: ## Create Python virtual environment
	mkdir -p env
	virtualenv -p `which python3.5` env/

pip-upgrade: ## Upgrade pip packages
	pip install --upgrade pip

pip-save: ## Save curretnly installed packages as requirements.frozen.txt
	pip freeze > www/requirements.frozen.txt

pip-install: ## Run pip install from requirements.frozen.txt
	pip install -r www/requirements.frozen.txt

.PHONY: help

help:
		@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
