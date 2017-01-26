#!/bin/sh

function start_app_preexecute {
  # Create secret key for django if does not exist
  if [ ! -r /srv/home/www/persistent/secret_key.txt ] ;then
    echo 'Generating Django secret key'
    python3 -c 'import os, binascii; print(binascii.hexlify(os.urandom(32)).decode())' > /srv/home/www/persistent/secret_key.txt
  fi

  # Initialize/migrate django database
  DJANGO_DB_LOCK_FILE=/srv/home/www/persistent/.db_initialized
  echo "=== Begin django database init `date -Iseconds` ==="

  cd /srv/home/www/
  if [ -f "${DJANGO_DB_LOCK_FILE}" ]; then
    echo "=== Database exist, doing migrate"

    pyenv python3 manage.py migrate --noinput

  else
    echo "=== Database initialization"

    pyenv python3 manage.py migrate --noinput
    pyenv python3 manage.py loaddata init
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@foggly.net', 'foggly-admin')" | pyenv python3 manage.py shell

  fi
  echo "=== End django database init `date -Iseconds` ==="

  touch "${DJANGO_DB_LOCK_FILE}"
}
