FROM foggly/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN apt-get clean && \
    apt-get update && \
    apt-get install -y apache2 libapache2-mod-php7.0 libapache2-mod-xsendfile php7.0 php7.0-mysql php7.0-curl php7.0-gd php7.0-opcache php7.0-json php7.0-mcrypt php7.0-intl php7.0-zip php7.0-bz2 php7.0-xml php7.0-mbstring php7.0-soap php7.0-readline php7.0-enchant php7.0-xmlrpc php7.0-sqlite3 php-imagick && \
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

RUN sed -i 's,;upload_tmp_dir =,upload_tmp_dir =/srv/home/tmp,;s,upload_max_filesize = 2M,upload_max_filesize = 1024M,;s,post_max_size = 8M,post_max_size = 0,' /etc/php/7.0/apache2/php.ini && \
    sed -i 's,mysqli\?\.default_socket *=,\0/var/lib/mysql/mysql.sock,;' /etc/php/7.0/apache2/php.ini /etc/php/7.0/cli/php.ini && \
    rm /etc/apache2/sites-available/default-ssl.conf && \
    rm /lib/systemd/system/apache2.service.d/apache2-systemd.conf

ADD local/  /usr/local/
ADD etc/  /etc/

ENV WWW_ROOT=$ROOT_DIR/www/ WWW_ROOT_SUBDIR=""

EXPOSE 3000
