# Nexus Portal CTF

## Overview
Nexus Portal is a vulnerable web application designed for capture-the-flag (CTF) educational purposes. It simulates a corporate portal with multiple hidden vulnerabilities that form an attack chain leading to full system compromise.

**Objective**: Starting as an unauthenticated external user, compromise the web application, pivot to the internal network, and escalate privileges to root on the internal server.

## Architecture
The lab consists of two Docker containers:
1.  **webapp (Nexus Portal)**: A python Flask application running the main portal.
2.  **internal_service**: A hidden internal service used for configuration processing (PyYAML).

## Installation & Deployment
1.  Ensure you have `docker` and `docker-compose` installed.
2.  Clone this repository.
3.  Build and start the lab:
    ```bash
    docker-compose up --build -d
    ```
4.  The application will be accessible at `http://localhost:80` (or `http://127.0.0.1:80`).
5.  **Attacker Setup**: Ensure your attacking machine (or script) can reach the container network. The configuration uses the subnet `10.100.100.0/24`. The attacker gateway is typically `10.100.100.1`.

## Scenario & Vulnerabilities

### 1. Account Takeover (CSRF)
The administrator regularly checks support tickets. The "Submit Ticket" feature allows sending a link to the admin.
- **Vulnerability**: Cross-Site Request Forgery (CSRF) in the `/make_admin` endpoint.
- **Goal**: Force the admin to visit a malicious page that promotes your user to admin.

### 2. Information Disclosure (LFI)
The Admin Panel includes a "Log Viewer" to debug the system.
- **Vulnerability**: Local File Inclusion (LFI).
- **Goal**: Guess the proper filename (`main.py`) to leak the source code and discover hidden secrets.

### 3. Remote Code Execution (DNS Rebinding/SSRF)
The source code reveals a hidden `/healthcheck` endpoint vulnerable to Command Injection, but it is protected:
1.  It only accepts requests from `127.0.0.1`.
2.  It requires a secret internal `X-Nexus-Token`.
The Admin Panel has an "External Link Scanner" that injects this token but blocks internal IPs.
- **Vulnerability**: DNS Rebinding (TOCTOU).
- **Goal**: Bypass the IP check to make the Scanner send the valid token to the local `/healthcheck` endpoint, executing commands.

### 4. Lateral Movement (PyYAML RCE)
From the compromised WebApp, you discover an "internal_service" on port 5000.
- **Vulnerability**: Insecure YAML Deserialization (PyYAML).
- **Goal**: Identify the YAML backend via error messages and send a malicious deserialization payload to `process_config` to gain a shell on the internal container.

### 5. Privilege Escalation (Python Library Hijacking)
The internal service runs as the `developer` user.
- **Vulnerability**: `sudo` misconfiguration allowing `developer` to run a Python script in a writable directory.
- **Goal**: Hijack a standard library module (like `shutil`) to execute code as root when the sudo script runs.

## Flags
- **Flag 1**: `SecRes{1st_flag_csrf_admin_access}` - Visible on the Admin Dashboard after CSRF.
- **Flag 2**: `SecRes{2nd_flag_lfi_source_leak}` - Found in `main.py` source code via LFI.
- **Flag 3**: `SecRes{3rd_flag_webapp_dns_rebind_rce}` - In `/home/Andy/flag.txt` (WebApp Container).
- **Flag 4**: `SecRes{4th_flag_internal_yaml_pivot}` - In `/home/developer/flag.txt` (Internal Service Container).
- **Flag 5**: `SecRes{5th_flag_root_python_hijacking}` - In `/root/flag.txt` (Internal Service Root).

## Disclaimer
This project is for educational purposes only. Do not use these techniques on systems you do not own or have explicit permission to test.
