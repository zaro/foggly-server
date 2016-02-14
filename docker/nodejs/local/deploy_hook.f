#!/bin/bash

function deploy_hook_init {

}

function deploy_hook_install {
  echo '*** BEGIN npm install in '`pwd`
  /usr/local/bin/npm install
  echo '*** END npm install'
}

function deploy_hook_reload {
  . /usr/local/procfile_to_supervisor

  /usr/bin/supervisorctl reread
  /usr/bin/supervisorctl update

}
