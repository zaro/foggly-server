#!/bin/bash

# FROM : https://github.com/catatnight/docker-postfix

postconf -e myhostname=$maildomain
postconf -e -F '*/*/chroot = n'
