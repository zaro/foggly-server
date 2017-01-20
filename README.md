foggly.net

## Building

In top dir:

    make all FULL=1

## Running on a single machine

### Setup

Setup firewall:

    # add docker interface to the trusted zone
    firewall-cmd --permanent --zone=trusted --change-interface=docker0
    # allow redis port
    firewall-cmd --permanent --zone=trusted --add-port=6379/tcp
    firewall-cmd --reload

It is good to disable docker iptables integration :

https://fralef.me/docker-and-iptables.html

or else all the ports that containers expose will be public.

Create directory for host_controller persistent storage:

```
    mkdir /srv/_host_controller
    chown 33.33 -R /srv/_host_controller/
    mkdir /srv/_host_worker
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

- Rebase the images on https://hub.docker.com/r/maci0/systemd/ and https://rhatdan.wordpress.com/2014/04/30/running-systemd-within-a-docker-container/
- or use [rkt](https://coreos.com/rkt/docs/latest/) instead of docker

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
