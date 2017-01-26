#!/bin/bash

function activate_pyvenv {

  if [ ! -f /srv/home/pyvenv/bin/activate ]; then
    pyvenv-3.5 --system-site-packages /srv/home/pyvenv

    . /srv/home/pyvenv/bin/activate
    pip3 install --upgrade pip
  fi

  . /srv/home/pyvenv/bin/activate

}

function deploy_hook_init {

  activate_pyvenv

 . /usr/local/path.add
}

function deploy_hook_install {
  if [ -f requirements.txt ]; then
    echo '*** BEGIN pip install in '`pwd`
    pip install -r requirements.txt
    echo '*** END pip install'
  fi
}


function deploy_hook_reload {
  systemctl restart web
}
