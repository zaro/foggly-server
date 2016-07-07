foggly.net

## Running

REDIS_URL should point to interface docker0 ip.

Host controller:

    docker run -d -h 'test.controller' -e 'REDIS_URL=redis://172.17.0.1' -p 3000:3000 -p 6379:6379  zaro/host_controller
    firewall-cmd --zone=public --add-port=6379/tcp

Host worker:

    docker run -d --privileged -h 'test.worker' -v /srv:/host_srv -v /var/run/docker.sock:/var/run/docker.sock -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket -e 'REDIS_URL=redis://172.17.0.1' -p 3001:3000  zaro/host_worker

## Development
flake8 and eslint configurations are included, to use them in Atom install :

    linter-flake8 linter-eslint
