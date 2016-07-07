#!/bin/bash

function activate_pyvenv {

  if [ ! -d /srv/home/pyvenv ]; then
    pyvenv-3.5 --system-site-packages /srv/home/pyvenv
  fi

  . /srv/home/pyvenv/bin/activate

}

function procfile_entry {
  if [[ "$1" == "web" ]]; then
    return 0
  fi
  return 1
}

function procfile_entry_append {
  FILE="$1"
  # echo "environment=PATH=/srv/home/pyvenv/bin:%(ENV_PATH)s" >> "${FILE}"
}
function procfile_comand {
  echo /usr/local/bin/pyenv "$@"
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
  echo '*** BEGIN generate supervisor entries'
  . /usr/local/procfile_to_supervisor
  procfile_process

  /usr/bin/supervisorctl reread
  /usr/bin/supervisorctl update
  echo '*** END generate supervisor entries'

  /usr/bin/supervisorctl restart web
}
