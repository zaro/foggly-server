#!/bin/bash

function deploy_hook_init {
  return 0
}

function deploy_hook_install {
  echo '*** BEGIN npm install in '`pwd`
  /usr/local/bin/npm install
  echo '*** END npm install'
}

function deploy_hook_reload {

  /usr/bin/supervisorctl restart web

}
