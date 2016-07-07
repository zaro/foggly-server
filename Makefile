all: base nodejs python php7

base: ## build the base container
	cd docker/base && docker build -t zaro/base .

nodejs: ## build nodejs app runtime container
	cd docker/nodejs && docker build -t zaro/nodejs .

php7: ## build php app runtime container
	cd docker/php7 && docker build -t zaro/php7 .

python: ## build python app runtime container
	cd docker/python && docker build -t zaro/python .

host_controller: ## build the host_controller container
	cd site/www && docker build -f Dockerfile.host_controller -t zaro/host_controller .

host_worker: ## build the host_worker container
	cd site/www && docker build -f Dockerfile.host_worker -t zaro/host_worker .

clean_junk_images: ## clean all non-tagged docker images
	docker rmi `docker images | grep '^<none>' | awk '{ print $3 }'`

.PHONY: base nodejs php7 python host_controller host_worker

	help:
			@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
