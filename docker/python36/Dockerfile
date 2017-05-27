FROM foggly/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0x5bb92c09db82666c
RUN echo deb http://ppa.launchpad.net/fkrull/deadsnakes/ubuntu xenial main   | tee /etc/apt/sources.list.d/python3.6.list

RUN apt-get update && \
    apt-get install -y uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev python3.6 python3.6-venv python3.6-dev make gcc g++ build-essential libssl-dev libffi-dev&& \
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

# Install pip
RUN cd /tmp; curl -O https://bootstrap.pypa.io/get-pip.py; python3.6 get-pip.py

RUN  PYTHON=python3.6 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36" && \
     mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so && \
     chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so

ADD local/  /usr/local/
ADD etc/  /etc/

ENV WWW_ROOT=$ROOT_DIR/www/

EXPOSE 3000
