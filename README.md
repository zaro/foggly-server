foggly.net

## Building

In top dir:

    make all FULL=1

## Running on a single machine

### Setup

Disable docker iptables integration :

https://fralef.me/docker-and-iptables.html
or else all the ports that containers expose will be public.

add --iptables=false to docker daemon startup
dockerd --iptables=false

Setup firewall:

    # masquerade traffic to containers
    firewall-cmd --permanent --zone=public --add-masquerade
    # add docker interface to the trusted zone
    firewall-cmd --permanent --zone=trusted --change-interface=docker0
    # allow redis port
    firewall-cmd --permanent --zone=public --add-port=80/tcp
    firewall-cmd --permanent --zone=trusted --add-port=6379/tcp
    firewall-cmd --reload

Create directory for host_controller persistent storage:

```
    mkdir -p /srv/_host_controller/log
    chown 33.33 -R /srv/_host_controller/
    mkdir -p /srv/_host_worker/log
    chown 33.33 -R /srv/_host_worker/
```

### Run with systemd

    cp systemd/foggly-host-* /etc/systemd/system/
    systemctl start foggly-host-worker.service
    systemctl start foggly-host-controller.service

    # if you want them to start at boot
    systemctl enable foggly-host-controller.service
    systemctl enable foggly-host-worker.service

### Run Manually

Host controller:

```
    docker run -d --name 'host_controller' -h 'test.controller' -v /srv/_host_controller:/srv/home/www/persistent -e 'REDIS_URL=redis://172.17.0.1' -p 3000:3000 -p 6379:6379  foggly/host_controller
```

Host worker:

```
    docker run -d --privileged --name 'host_worker' -h '<MASTER_DOMAIN>' -v /srv:/host_srv -v /srv/_host_worker:/srv/home/www/persistent -v /var/run/docker.sock:/var/run/docker.sock -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket  -v /var/lib/mysql/:/var/lib/mysql/ -e 'REDIS_URL=redis://172.17.0.1' -p 3001:3000  foggly/host_worker
```

REDIS_URL should point to interface docker0 ip.

MASTER_DOMAIN - can be anything, but it should be the domain that's listed in Reverse DNS record, because it is used both to identify the worker in the controller (Host -> Main domain), and for SMTP configuration.

## Development
flake8 and eslint configurations are included, to use them in Atom install :

    linter-flake8 linter-eslint

## Mail setup

This link: https://blog.codinghorror.com/so-youd-like-to-send-some-email-through-code/
http://www.spfwizard.net/
https://support.google.com/mail/answer/81126

## Known bugs

-  The status of the domains on the Domains screen is unreliable

## Todo

- Investigate https://github.com/oderwat/hubic2swiftgate , for backup using duplicity
- make a demo using : https://dply.co/button

## DB Notes

create postgres foggly user :

```
sudo -u postgres -s
psql template1
CREATE ROLE foggly SUPERUSER LOGIN PASSWORD 'very_secret_pass';
```

change pg_hba.conf :
```
#from
local   all             all                                     peer

#to
local   all             postgres                                peer
local   all             all                                     md5
```

mysql on Centos:

```
$ cat /usr/lib/tmpfiles.d/mysql.conf
d /var/run/mysqld 0755 mysql mysql -

$ cat  /etc/my.cnf
[mysqld]
datadir=/var/lib/mysql
#socket=/var/lib/mysql/mysql.sock
socket=/var/run/mysqld/mysqld.sock
# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0
# Settings user and group are ignored when systemd is used.
# If you need to run mysqld under a different user or group,
# customize your systemd unit file for mariadb according to the
# instructions in http://fedoraproject.org/wiki/Systemd

[mysqld_safe]
log-error=/var/log/mariadb/mariadb.log
pid-file=/var/run/mariadb/mariadb.pid

#
# include all files from the config directory
#
!includedir /etc/my.cnf.d

$ cat /etc/my.cnf.d/client.cnf
#
# These two groups are read by the client library
# Use it for options that affect all clients, but not the server
#


[client]
socket=/var/run/mysqld/mysqld.sock

# This group is not read by mysql client library,
# If you use the same .cnf file for MySQL and MariaDB,
# use it for MariaDB-only client options
[client-mariadb]
```
