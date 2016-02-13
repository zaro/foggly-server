all: base nodejs php7

base:
	cd base && docker build -t zaro/base .

nodejs:
	cd nodejs && docker build -t zaro/nodejs .

php7:
	cd php7 && docker build -t zaro/php7 .

python:
	cd python && docker build -t zaro/python .

.PHONY: base nodejs php7 python
