#!/bin/bash

function deploy_hook_init {
}

function deploy_hook_install {
  echo '*** BEGIN composer install in '`pwd`
  if /usr/local/bin/composer --no-check-publish  -n -q validate; then
          /usr/local/bin/composer install
          /usr/local/bin/composer update
  fi
  echo '*** END composer install'
}

function deploy_hook_reload {
}
