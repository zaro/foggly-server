#!/bin/bash

function procfile_entry {
  return 1
}

function deploy_hook_init {
  return 0
}

function deploy_hook_install {
  return 0
}


function deploy_hook_reload {
  sudo systemctl restart web
}
