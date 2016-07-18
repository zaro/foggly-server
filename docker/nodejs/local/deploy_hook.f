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
  echo '*** BEGIN generate supervisor entries'
  . /usr/local/procfile_to_supervisor

  /usr/bin/supervisorctl reread
  /usr/bin/supervisorctl update
  echo '*** END generate supervisor entries'

  /usr/bin/supervisorctl restart web

}
