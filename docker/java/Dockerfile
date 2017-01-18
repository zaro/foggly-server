FROM foggly/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN apt-get update && \
    mkdir -p /usr/share/man/man1/ && \
    apt-get install -y openjdk-8-jdk-headless maven && \
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
