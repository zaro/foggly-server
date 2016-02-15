#!/bin/bash

function deploy_hook_init {
}

# More info on how composer install vs update work:
#    https://adamcod.es/2013/03/07/composer-install-vs-composer-update.html#fn2
function deploy_hook_install {
  echo '*** BEGIN composer install in '`pwd`
  /usr/local/bin/composer install
  echo '*** END composer install'
}

function deploy_hook_reload {
}
