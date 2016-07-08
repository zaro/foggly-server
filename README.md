foggly.net

## Building

In site/www:

    npm install
    bower install
    ./manage.py collectstatic
    node_modules/.bin/webpack --progress --colors
    ./manage.py collectstatic # run it second time to collect webpack bundles

In top dir:

    make all

## Running on a single machine

Setup firewall:

    # add docker interface to the trusted zone
    firewall-cmd --permanent --zone=trusted --change-interface=docker0
    # allow redis port
    firewall-cmd --permanent --zone=trusted --add-port=6379/tcp
    firewall-cmd --reload

Create directory for host_controller persistent storage:

    mkdir /srv/_host_controller
    chown 33.33 -R /srv/_host_controller/

Host controller:

    docker run -d -h 'test.controller' -v /srv/_host_controller:/srv/home/www/persistent -e 'REDIS_URL=redis://172.17.0.1' -p 3000:3000 -p 6379:6379  foggly/host_controller

Host worker:

    docker run -d --privileged -h 'test.worker' -v /srv:/host_srv -v /var/run/docker.sock:/var/run/docker.sock -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket  -v /var/lib/mysql/:/var/lib/mysql/ -e 'REDIS_URL=redis://172.17.0.1' -p 3001:3000  foggly/host_worker

REDIS_URL should point to interface docker0 ip.

## Development
flake8 and eslint configurations are included, to use them in Atom install :

    linter-flake8 linter-eslint
