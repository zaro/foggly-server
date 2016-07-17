all: base nodejs python php php5 host_controller host_worker

base: ## build the base container
	cd docker/base && docker build -t foggly/base .

nodejs: ## build nodejs app runtime container
	cd docker/nodejs && docker build -t foggly/nodejs .

php: ## build php app runtime container
	cd docker/php && docker build -t foggly/php .

php5: ## build php5 app runtime container
	cd docker/php5 && docker build -t foggly/php5 .

python: ## build python app runtime container
	cd docker/python && docker build -t foggly/python .

host_controller: ## build the host_controller container
	node -e 'try{s = JSON.parse(require("fs").readFileSync("site/www/webpack-stats.json")).status;} catch(e){s=null}; if(s !== "done"){console.log("Webpack bundles not compiled"); process.exit(1) }'
	#cd site/www && ./manage.py collectstatic --noinput
	#cd site/www && node_modules/.bin/webpack --progress --colors
	#cd site/www && ./manage.py collectstatic --noinput
	cd site/www && docker build -f Dockerfile.host_controller -t foggly/host_controller .

host_worker: ## build the host_worker container
	cd site/www && docker build -f Dockerfile.host_worker -t foggly/host_worker .

clean_junk_images: ## clean all non-tagged docker images
	docker rmi `docker images -f dangling=true --format="{{.ID}}"`

rm_stopped_containers: ## remove all stopped containers
	docker rm `docker ps -f status=exited -q`

.PHONY: base nodejs php7 python host_controller host_worker

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
