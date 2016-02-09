FROM zaro/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0x5a16e7281be7a449
RUN echo deb http://dl.hhvm.com/ubuntu wily main | tee /etc/apt/sources.list.d/hhvm.list

RUN apt-get clean && \
    apt-get update && \
    apt-get install -y hhvm  && \
    apt-get clean && \
    rm -rf /usr/share/locale/* \
      /usr/share/doc/* \
      /usr/share/man/* \
      /usr/share/groff/* \
      /usr/share/info/* \
      /usr/share/lintian/* \
      /usr/share/linda/*  && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/log/*.log && \
    mkdir -p /var/run/sshd /var/log/supervisor

COPY php.ini /etc/hhvm/php.ini
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV ROOT_DIR=/srv/home
ENV WWW_ROOT=$ROOT_DIR/www \
    WWW_RUN_DIR=$ROOT_DIR/run \
    WWW_CFG_DIR=$ROOT_DIR/cfg \
    PHP_INI=/etc/hhvm/php.ini \
    NGINX_USER=www-data \
    NGINX_UID=996 \
    NGINX_GID=995

# hhvm uses fuser command from psmisc
RUN groupadd --gid "${NGINX_GID}" "${NGINX_USER}" && \
    useradd --uid ${NGINX_UID} --gid ${NGINX_GID} --create-home --home-dir /srv/home ${NGINX_USER} && \
    chown -R "${NGINX_USER}"."${NGINX_USER}" /var/run/hhvm/

COPY run_hhvm /

EXPOSE 22
CMD ["/usr/bin/supervisord", "-c", "/srv/home/etc/supervisor/supervisord.conf"]
