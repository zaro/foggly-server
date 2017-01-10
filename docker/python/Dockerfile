FROM foggly/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN apt-get update && \
    apt-get install -y uwsgi uwsgi-plugin-python3 python3.5 python3.5-venv python3.5-dev python3-setuptools python3-wheel python3-cffi python3-cryptography python3-simplejson python3-anyjson python3-psycopg2 make gcc g++&& \
    apt-get clean && \
    rm -rf /usr/share/locale/* \
      /usr/share/doc/* \
      /usr/share/man/* \
      /usr/share/groff/* \
      /usr/share/info/* \
      /usr/share/lintian/* \
      /usr/share/linda/*  && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/log/*.log

ADD local/  /usr/local/
ADD etc/  /etc/

ENV WWW_ROOT=$ROOT_DIR/www/

EXPOSE 3000
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
