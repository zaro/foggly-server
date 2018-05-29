#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
    echo "This script uses functionality which requires root privileges"
    exit 1
fi

acbuild --debug begin

acbuild --debug set-name foggly.net/base


acbuild --debug dep add tklx.org/base:0.1.1


acbuild  --debug copy dpkg_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc

acbuild --debug run -- echo "postfix postfix/mailname string example.com" | debconf-set-selections
acbuild --debug run -- echo "postfix postfix/main_mailer_type string \'Internet Site\'" | debconf-set-selections
acbuild --debug run -- apt-get update \&\& \
    apt-get install -y psmisc nano less vim rsync supervisor postfix curl mariadb-client-core-10.0 libmariadb-client-lgpl-dev redis-server \&\& \
    apt-get install -y --no-install-recommends git make openssh-server rsyslog opendkim opendkim-tools \&\& \
    apt-get clean \&\& \
    rm -fr /etc/postfix \&\& \
    ln -s /srv/home/etc/postfix/ /etc/postfix \&\& \
    rm -rf /usr/share/locale/* \
      /usr/share/doc/* \
      /usr/share/man/* \
      /usr/share/groff/* \
      /usr/share/info/* \
      /usr/share/lintian/* \
      /usr/share/linda/*  \&\& \
    rm -rf /var/lib/apt/lists/* \&\& \
    rm -rf /var/log/*.log \&\& \
    mkdir -p /var/run/sshd \&\& \
    ln -s /srv/home/www /www \&\& \
    ln -s /usr/bin/mariadb_config /usr/bin/mysql_config \&\& \
    printf "\n[client]\nsocket = /var/lib/mysql/mysql.sock\n" \>\> /etc/mysql/my.cnf \&\& \
    usermod -d /srv/home/ -s /bin/bash www-data \&\& \
    curl -o /usr/local/bin/rmate https://raw.githubusercontent.com/aurora/rmate/master/rmate \&\& \
    chmod a+x /usr/local/bin/rmate

acbuild --debug copy  local/  /usr/local/
acbuild --debug copy  etc/  /etc/

acbuild --debug environment add ROOT_DIR /srv/home

acbuild --debug port add ssh tcp 22
acbuild --debug set-exec -- /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

acbuild --debug write --overwrite foggly-base-linux-amd64.aci
