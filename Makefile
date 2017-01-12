all: base nodejs python php php5 java host_controller host_worker

base: ## build the base container
	cd docker/base && docker build -t foggly/base .

nodejs: base ## build nodejs app runtime container
	cd docker/nodejs && docker build -t foggly/nodejs .

php: base ## build php app runtime container
	cd docker/php && docker build -t foggly/php .

php5: base ## build php5 app runtime container
	cd docker/php5 && docker build -t foggly/php5 .

python: nodejs ## build python app runtime container
	cd docker/python && docker build -t foggly/python .

java: nodejs ## build java app runtime container
		cd docker/java && docker build -t foggly/java .

host_controller:  python ## build the host_controller container
	if [ "${FULL}" ]; then \
		cd site/www ; \
		npm install ; \
		bower --allow-root install ; \
		./manage.py collectstatic --noinput; \
		node_modules/.bin/webpack --progress --colors; \
		./manage.py collectstatic --noinput; \
	fi
	node -e 'try{s = JSON.parse(require("fs").readFileSync("site/www/webpack-stats.json")).status;} catch(e){s=null}; if(s !== "done"){console.log("Webpack bundles not compiled"); process.exit(1) }'
	cd site/www && docker build -f Dockerfile.host_controller -t foggly/host_controller .

host_worker: python ## build the host_worker container
	cd site/www && docker build -f Dockerfile.host_worker -t foggly/host_worker .

clean_junk_images: ## clean all non-tagged docker images
	docker rmi `docker images -f dangling=true --format="{{.ID}}"`

rm_stopped_containers: ## remove all stopped containers
	docker rm `docker ps -f status=exited -q`

.PHONY: base nodejs python php php5 java host_controller host_worker

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
