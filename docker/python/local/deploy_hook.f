#!/bin/bash

function activate_pyvenv {

  if [ ! -f /srv/home/pyvenv/bin/activate ]; then
    pyvenv-3.5 --system-site-packages /srv/home/pyvenv

    . /srv/home/pyvenv/bin/activate
    pip3 install --upgrade pip
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
  if [ -f requirements.txt ]; then
    echo '*** BEGIN pip install in '`pwd`
    pip install -r requirements.txt
    echo '*** END pip install'
  fi
}

function deploy_hook_user_hook {
  if [ -x .hooks/on_deploy ]; then
    echo '*** BEGIN on_deploy '`pwd`
    .hooks/on_deploy
    echo '*** END on_deploy'
  fi
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
