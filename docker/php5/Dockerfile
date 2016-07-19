FROM foggly/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>
RUN apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0x4F4EA0AAE5267A6C
RUN echo deb http://ppa.launchpad.net/ondrej/php/ubuntu xenial main  | tee /etc/apt/sources.list.d/php7.list


RUN apt-get clean && \
    apt-get update && \
    apt-get install -y apache2 libapache2-mod-php5.6 libapache2-mod-xsendfile php5.6 php5.6-mysql php5.6-curl php5.6-gd php5.6-opcache php5.6-json php5.6-mcrypt php5.6-intl php5.6-zip php5.6-bz2 php5.6-xml php5.6-mbstring php5.6-soap php5.6-readline php5.6-enchant php5.6-xmlrpc php5.6-sqlite3 && \
    apt-get clean && \
    a2enmod rewrite && \
    (cd /usr/local/bin; curl -sS https://getcomposer.org/installer | php; ln -s composer.phar composer) && \
    sed -i 's,Listen *80,Listen 3000,;' /etc/apache2/ports.conf && \
    rm -rf /usr/share/locale/* \
      /usr/share/doc/* \
      /usr/share/man/* \
      /usr/share/groff/* \
      /usr/share/info/* \
      /usr/share/lintian/* \
      /usr/share/linda/*  && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/log/*.log

RUN sed -i 's,;upload_tmp_dir =,upload_tmp_dir =/srv/home/tmp,;s,upload_max_filesize = 2M,upload_max_filesize = 1024M,;s,post_max_size = 8M,post_max_size = 0,' /etc/php/5.6/apache2/php.ini && \
    sed -i 's,mysqli\?\.default_socket *=,\0/var/lib/mysql/mysql.sock,;' /etc/php/5.6/apache2/php.ini /etc/php/5.6/cli/php.ini && \
    rm /etc/apache2/sites-available/default-ssl.conf

ADD local/  /usr/local/
ADD etc/  /etc/

ENV WWW_ROOT=$ROOT_DIR/www/ WWW_ROOT_SUBDIR=""

EXPOSE 3000
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
