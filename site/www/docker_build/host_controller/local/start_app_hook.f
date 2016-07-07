
function start_app_preexecute {
  if [ ! -r /srv/home/secret_key.txt ] ;then
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1 > /srv/home/secret_key.txt
  fi
}
