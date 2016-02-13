FROM zaro/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0x4F4EA0AAE5267A6C
RUN echo deb http://ppa.launchpad.net/ondrej/php/ubuntu wily main  | tee /etc/apt/sources.list.d/php7.list

RUN apt-get clean && \
    apt-get update && \
    apt-get install -y php7.0 php7.0-mysql php7.0-curl php7.0-gd php7.0-opcache php7.0-json php7.0-mcrypt php7.0-intl && \
    apt-get clean && \
    a2enmod rewrite && \
    (cd /usr/local/bin; curl -sS https://getcomposer.org/installer | php; ln -s composer.phar composer) && \
    sed -i 's,mysqli\?\.default_socket *=,\0/var/lib/mysql/mysql.sock,;' /etc/php/7.0/apache2/php.ini /etc/php/7.0/cli/php.ini && \
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

#apache config
COPY default_site.conf /etc/apache2/sites-available/000-default.conf
RUN sed -i 's,;upload_tmp_dir =,upload_tmp_dir =/srv/home/tmp,;s,upload_max_filesize = 2M,upload_max_filesize = 1024M,;s,post_max_size = 8M,post_max_size = 0,' /etc/php/7.0/apache2/php.ini && \
    rm /etc/apache2/sites-available/default-ssl.conf

COPY deploy_container /usr/local/deploy_container.d/10-php7
COPY supervisord-php7.conf /etc/supervisor/conf.d/supervisord-php7.conf
COPY deploy_hook /usr/local/deploy_hook

ENV WWW_ROOT=$ROOT_DIR/www/ WWW_ROOT_SUBDIR=""

EXPOSE 3000
CMD ["/usr/bin/supervisord"]
