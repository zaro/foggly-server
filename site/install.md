For Centos :

    yum install python34-devel mariadb-devel


## Deployment
Static files:

    ./manage.py bower_install -- --allow-root # allow-root root needed only when running as root
    ./manage.py collectstatic
