FROM ubuntu:xenial

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

COPY dpkg_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc

RUN echo "postfix postfix/mailname string example.com" | debconf-set-selections
RUN echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y psmisc nano supervisor postfix curl mariadb-client-core-10.0 && \
    apt-get install -y --no-install-recommends git openssh-server rsyslog && \
    apt-get clean && \
    rm -fr /etc/postfix && \
    ln -s /srv/home/etc/postfix/ /etc/postfix && \
    rm -rf /usr/share/locale/* \
      /usr/share/doc/* \
      /usr/share/man/* \
      /usr/share/groff/* \
      /usr/share/info/* \
      /usr/share/lintian/* \
      /usr/share/linda/*  && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/log/*.log && \
    mkdir -p /var/run/sshd && \
    ln -s /srv/home/www /www && \
    printf "\n[client]\nsocket = /var/lib/mysql/mysql.sock\n" >> /etc/mysql/my.cnf && \
    useradd -d /srv/home/ -M -N -g www-data -u 33 -o -s /bin/bash user

ADD local/  /usr/local/
ADD etc/  /etc/

ENV ROOT_DIR=/srv/home

EXPOSE 22
CMD ["/usr/bin/supervisord"]
