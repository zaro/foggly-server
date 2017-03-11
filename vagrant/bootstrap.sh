#!/usr/bin/env bash

# Install basic operating system packages
apt-get update -y
apt-get install -y --force-yes curl mariadb-server  nginx firewalld postgresql libpq-dev build-essential \
      python3-pip mariadb-client-core-10.0 libmariadb-client-lgpl-dev python3.5 python3.5-venv \
      python3.5-dev python3-setuptools python3-wheel python3-cffi python3-cryptography python3-simplejson \
      python3-anyjson python3-psycopg2 python3-mysqldb python3-crypto htop

ln -s /usr/bin/mariadb_config /usr/bin/mysql_config

# Install nodejs
(
cd /tmp/
set -ex \
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

export NPM_CONFIG_LOGLEVEL=info
export NODE_VERSION=7.4.0

export NODE_ARCH=$(uname -m | sed 's/aarch64/arm64/;s/x86_64/x64/')
curl -SLO "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.gz"
curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc"
gpg --verify SHASUMS256.txt.asc
grep " node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c -
tar -xzf "node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz" -C /usr/local --strip-components=1
rm "node-v$NODE_VERSION-linux-$NODE_ARCH.tar.gz" SHASUMS256.txt.asc
)

systemctl enable mariadb
systemctl start mariadb

systemctl enable postgresql
systemctl start postgresql


curl -fsSL https://get.docker.com/ | sh

sudo usermod -aG docker ubuntu

systemctl enable docker
systemctl start docker

sed -i "/include.*sites-enabled/a \
      include /srv/*/*/etc/site.conf;" /etc/nginx/nginx.conf
systemctl enable nginx
systemctl start nginx
echo "*** Done ***"