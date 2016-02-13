#!/bin/bash

function activate_pyvenv {

  if [ ! -d /srv/home/pyvenv ]; then
    pyvenv /srv/home/pyvenv
  fi

  . /srv/home/pyvenv/bin/activate

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
  /usr/bin/supervisorctl restart web
}
