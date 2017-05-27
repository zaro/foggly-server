all: base nodejs python python36 php php5 java host_controller host_worker


docker_%:
	cd docker/$* && docker build -t foggly/$* .

images/%.tar:
	@if [ "$(TAR_IMAGES)" ]; then  \
		echo -n "Exporting $*.tar ... "; \
		mkdir -p images/;\
		docker export "$$(docker create foggly/$* true)" > images/$*.tar;\
		echo "DONE"; \
	else true; fi

# Build docker and tar image (disabled right now)
build_runtime_%: docker_% # images/%.tar
	@echo Done building $*

base: build_runtime_base ## build the base container

nodejs: base build_runtime_nodejs ## build nodejs app runtime container

php: base build_runtime_php ## build php app runtime container

php5: base build_runtime_php5 ## build php5 app runtime container

python: base build_runtime_python ## build python app runtime container

python36: base build_runtime_python36 ## build python3.6 app runtime container

java: base build_runtime_java ## build java app runtime container

host_controller: build_runtime_python ## build the host_controller container
	if [ "${FULL}" ]; then \
		cd site/www ; \
		npm install ; \
		node_modules/.bin/bower --allow-root install ; \
		./manage.py collectstatic --noinput; \
		node_modules/.bin/webpack --progress --colors; \
		./manage.py collectstatic --noinput; \
	fi
	node -e 'try{s = JSON.parse(require("fs").readFileSync("site/www/webpack-stats.json")).status;} catch(e){s=null}; if(s !== "done"){console.log("Webpack bundles not compiled"); process.exit(1) }'
	cd site/www && docker build -f Dockerfile.host_controller -t foggly/host_controller .

host_worker: build_runtime_python ## build the host_worker container
	cd site/www && docker build -f Dockerfile.host_worker -t foggly/host_worker .

clean_junk_images: ## clean all non-tagged docker images
	docker rmi `docker images -f dangling=true --format="{{.ID}}"`

rm_stopped_containers: ## remove all stopped containers
	docker rm `docker ps -f status=exited -q`

.PHONY: base nodejs python php php5 java host_controller host_worker docker_% build_runtime_%
.PRECIOUS: images/%.tar

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
