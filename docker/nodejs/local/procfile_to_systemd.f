#!/bin/sh

if [ "$(type -t procfile_entry)" != "function" ]; then
function procfile_entry {
  if [[ "$1" == "web" ]]; then
    return 0
  fi
  return 1
}
fi
