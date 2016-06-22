#!/bin/bash

function activate_pyvenv {

  if [ ! -d /srv/home/pyvenv ]; then
    pyvenv-3.5 /srv/home/pyvenv
  fi

  . /srv/home/pyvenv/bin/activate

}

function procfile_entry {
  if [[ "$1" != "web" ]]; then
    procfile_entry_to_supervisor "$@"
  fi
}

function deploy_hook_init {

  activate_pyvenv

}

function deploy_hook_install {
  echo '*** BEGIN pip install in '`pwd`
  pip install -r requirements.txt
  echo '*** END pip install'
}

function deploy_hook_reload {
  . /usr/local/procfile_to_supervisor

  /usr/bin/supervisorctl reread
  /usr/bin/supervisorctl update

  /usr/bin/supervisorctl restart web
}
