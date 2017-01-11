#!/bin/bash

function deploy_hook_init {
  export PATH=`pwd`/node_modules/.bin/:$PATH
}

function deploy_hook_install {
  echo '*** BEGIN npm install in '`pwd`
  npm install
  echo '*** END npm install'
}

function deploy_hook_reload {

  /usr/bin/supervisorctl restart web

}
