FROM foggly/base:latest

MAINTAINER "Svetlozar Argirov" <zarrro@gmail.com>

RUN add-apt-repository ppa:ondrej/php && \
    apt-get clean && \
    apt-get update && \
    apt-get install -y apache2 libapache2-mod-php7.2 libapache2-mod-xsendfile php7.2 php7.2-mysql php7.2-curl php7.2-gd php7.2-opcache php7.2-json php7.2-intl php7.2-zip php7.2-bz2 php7.2-xml php7.2-mbstring php7.2-soap php7.2-readline php7.2-enchant php7.2-xmlrpc php7.2-sqlite3 php-imagick && \
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

RUN sed -i 's,memory_limit = 128M,memory_limit = 512M,;s,;upload_tmp_dir =,upload_tmp_dir =/srv/home/tmp,;s,upload_max_filesize = 2M,upload_max_filesize = 1024M,;s,post_max_size = 8M,post_max_size = 0,' /etc/php/7.2/apache2/php.ini && \
    rm /etc/apache2/sites-available/default-ssl.conf && \
    rm /lib/systemd/system/apache2.service.d/apache2-systemd.conf

ADD local/  /usr/local/
ADD etc/  /etc/

ENV WWW_ROOT=$ROOT_DIR/www/ WWW_ROOT_SUBDIR=""

EXPOSE 3000
