#!/bin/sh

if [ "$(type -t procfile_entry)" != "function" ]; then
function procfile_entry {
  if [[ "$1" == "web" ]]; then
    return 0
  fi
  return 1
}
fi

if [ "$(type -t procfile_comand)" != "function" ]; then
function procfile_comand {
  echo /usr/local/bin/pyenv "$@"
}
fi
