#!/bin/bash

function deploy_hook_init {
  . /usr/local/path.add
}

function deploy_hook_install {
  echo '*** BEGIN npm install in '`pwd`
  if [ -f package.json ]; then
    npm install
  fi
  echo '*** END npm install'
}

function deploy_hook_reload {

  systemctl restart web

}
