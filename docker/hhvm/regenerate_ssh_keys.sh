ssh-keygen -q -f "/etc/ssh/ssh_host_rsa_key" -N '' -t rsa
ssh-keygen -q -f "/etc/ssh/ssh_host_dsa_key" -N '' -t dsa
ssh-keygen -q -f "/etc/ssh/ssh_host_ecdsa_key" -N '' -t ecdsa
ssh-keygen -q -f "/etc/ssh/ssh_host_ed25519_key" -N '' -t ed25519
