#!/usr/bin/env bash

apt-get update -y
apt-get install -y --force-yes curl mariadb-server  nginx firewalld postgresql libpq-dev

systemctl enable mariadb
systemctl start mariadb

systemctl enable postgresql
systemctl start postgresql


curl -fsSL https://get.docker.com/ | sh

sudo usermod -aG docker vagrant

systemctl enable docker
systemctl start docker

sed -i "/include.*sites-enabled/a \
      include /srv/*/*/etc/site.conf;" /etc/nginx/nginx.conf
systemctl enable nginx
systemctl start nginx
echo "*** Done ***"
