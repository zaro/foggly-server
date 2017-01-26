FROM aarch64/ubuntu:xenial

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>
ENV container=docker LC_ALL=C DEBIAN_FRONTEND=noninteractive

COPY dpkg_nodoc /etc/dpkg/dpkg.cfg.d/01_nodoc
COPY apt_config /etc/apt/apt.conf.d/01_buildconfig

RUN apt-get update && apt-get install curl

RUN echo "deb http://nginx.org/packages/mainline/ubuntu/ xenial nginx" > /etc/apt/sources.list.d/nginx.list
RUN curl http://nginx.org/keys/nginx_signing.key | apt-key add
RUN apt-get update && \
    apt-get install -y nginx && \
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
    rm -f /etc/machine-id

ADD local/  /usr/local/
ADD etc/  /etc/

RUN ln -s /usr/local/procfile_unit_generator /lib/systemd/system-generators/procfile_unit_generator
RUN systemctl set-default multi-user.target

ENV init /lib/systemd/systemd
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/lib/systemd/systemd"]
