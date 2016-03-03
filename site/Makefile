
env-create: ## Create Python virtual environment
	mkdir -p env
	virtualenv -p `which python3.5` env/

pip-upgrade: ## Upgrade pip packages
	pip install --upgrade pip

pip-save: ## Save curretnly installed packages as requirements.txt
	pip freeze > requirements.txt

pip-install: ## Run pip install
	pip install -r requirements.txt

.PHONY: help

help:
		@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
