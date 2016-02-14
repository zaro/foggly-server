all: base nodejs python php7

base:
	cd base && docker build -t zaro/base .

nodejs:
	cd nodejs && docker build -t zaro/nodejs .

php7:
	cd php7 && docker build -t zaro/php7 .

python:
	cd python && docker build -t zaro/python .

clean_junk_images:
	docker rmi `docker images | grep '^<none>' | awk '{ print $3 }'`

.PHONY: base nodejs php7 python
