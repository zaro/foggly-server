#!/usr/bin/env bash

apt-get update -y
apt-get install -y curl mariadb-server python3-pip python3-docker python3-jinja2 python3-mysqldb nginx firewalld

pip3 install celery
pip3 install redis
pip3 install hiredis

systemctl enable mariadb
systemctl start mariadb

ln -sf /usr/bin/python3.5 /usr/bin/python3

curl -fsSL https://get.docker.com/ | sh

sudo usermod -aG docker vagrant

mkdir -p /etc/systemd/system/docker.service.d/
cat <<EOS >/etc/systemd/system/docker.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/docker daemon -H fd:// -H tcp://0.0.0.0:2375
EOS

systemctl enable docker
systemctl start docker

sed -i "/include.*sites-enabled/a \
      include /srv/*/*/etc/site.conf" /etc/nginx/nginx.conf
systemctl enable nginx
systemctl start nginx
echo "*** Done ***"
