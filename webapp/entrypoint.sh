#!/bin/bash

export ADMIN_PASSWORD=87654321

useradd -ms /bin/bash Andy
echo "Andy:$ADMIN_PASSWORD" | chpasswd

/usr/sbin/sshd -D -E /var/log/sshd.log &

cd /app

python3 main.py