FROM ubuntu:xenial

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>
ENV container=docker LC_ALL=C DEBIAN_FRONTEND=noninteractive

COPY dpkg_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc
COPY apt_config /etc/apt/apt.conf.d/01_buildconfig

RUN echo "postfix postfix/mailname string example.com" | debconf-set-selections
RUN echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN apt-get clean && \
    apt-get update && \
    apt-get install -y ca-certificates curl psmisc nano less vim unzip rsync postfix mariadb-client-core-10.0 libmariadb-client-lgpl-dev redis-server && \
    apt-get install -y git make openssh-server opendkim opendkim-tools && \
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
    ln -s /usr/bin/mariadb_config /usr/bin/mysql_config && \
    usermod -d /srv/home/ -s /bin/bash www-data && \
    curl -o /usr/local/bin/rmate https://raw.githubusercontent.com/aurora/rmate/master/rmate && \
    chmod a+x /usr/local/bin/rmate

RUN set -ex \
  && for key in \
    9554F04D7259F04124DE6B476D5A82AC7E37093B \
    94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
    0034A06D9D9B0064CE8ADF6BF1747F4AD2306D93 \
    FD3A5288F042B6850C66B31F09FE44734EB7990E \
    71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
    DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
    B9AE9905FFD7803F25714661B63B535A4C206CA9 \
    C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
  ; do \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key"; \
  done

ENV NPM_CONFIG_LOGLEVEL info
ENV NODE_VERSION 7.4.0

RUN export NODE_ARCH=$(uname -m | sed 's/aarch64/arm64/;s/x86_64/x64/') \
  && curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz" \
  && curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
  && gpg --verify SHASUMS256.txt.asc \
  && grep " node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
  && tar -xzf "node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz" -C /usr/local --strip-components=1 \
  && rm "node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz" SHASUMS256.txt.asc

RUN cd /lib/systemd/system/sysinit.target.wants/; ls | grep -v 'systemd-tmpfiles-setup\|systemd-journal' | xargs rm -f $1; \
    rm -f /lib/systemd/system/multi-user.target.wants/*;\
    rm -f /lib/systemd/system/local-fs.target.wants/*; \
    rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
    rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
    rm -f /lib/systemd/system/basic.target.wants/*;\
    rm -f /lib/systemd/system/anaconda.target.wants/*; \
    rm -f /lib/systemd/system/plymouth*; \
    rm -f /lib/systemd/system/systemd-update-utmp*; \
    rm -f /etc/rc.local; \
    rm -f /lib/systemd/system/rc{.,-}local.service; \
    rm -rf /etc/systemd/system/timers.target.wants/; \
    rm -rf /etc/systemd/system/getty.target.wants/; \
    rm -rf /etc/systemd/system/sysinit.target.wants/; \
    rm -f /etc/init.d/ondemand; \
    rm -rf /etc/rc{0,1,2,3,4,5,6,S}.d; \
    rm -f /etc/machine-id; \
    rm -f /usr/lib/tmpfiles.d/systemd-nologin.conf

ADD local/  /usr/local/
ADD etc/  /etc/

RUN ln -s /usr/local/procfile_unit_generator /lib/systemd/system-generators/procfile_unit_generator
RUN systemctl set-default multi-user.target

ENV ROOT_DIR=/srv/home

EXPOSE 22

ENV init /lib/systemd/systemd
VOLUME [ "/sys/fs/cgroup" ]

# Terminate systemd with the proper signal (inits shutdown)
# "--stop-signal=$(kill -l RTMIN+3)
STOPSIGNAL 37
CMD ["/lib/systemd/systemd"]
