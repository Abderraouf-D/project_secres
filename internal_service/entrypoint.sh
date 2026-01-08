#!/bin/bash

# Start the SSH server
/usr/sbin/sshd -D -E /var/log/sshd.log &

python3 /app/app.py