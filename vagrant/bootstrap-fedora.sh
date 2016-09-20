#!/usr/bin/env bash

dnf install -y curl nodejs mariadb-server nginx firewalld

systemctl enable mariadb
systemctl start mariadb

ln -s /usr/bin/nodejs /usr/bin/node

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
      include /srv/*/*/etc/site.conf;" /etc/nginx/nginx.conf
systemctl enable nginx
systemctl start nginx
echo "*** Done ***"
