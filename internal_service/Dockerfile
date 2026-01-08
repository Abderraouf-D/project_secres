FROM python:3.9-slim

WORKDIR /app

# Install dependencies and sudo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -ms /bin/bash developer

# Copy app
COPY app.py .
COPY cleanup.py .
COPY user.txt /home/developer/flag.txt
COPY root.txt /root/flag.txt

# Set permissions
# Flag permissions
RUN chown -R developer:developer /app
RUN chmod 644 /home/developer/flag.txt
RUN chmod 600 /root/flag.txt

# Cleanup script (Root owned, world readable)
RUN chown root:root /app/cleanup.py
RUN chmod 755 /app/cleanup.py

# Sudoers configuration for PrivEsc (Python Library Hijacking)
# Allow developer to run /usr/bin/python3 /app/cleanup.py as root without password
# This allows hijacking via PYTHONPATH or writing to the directory if it's writable (it is /app owned by developer)
RUN echo "developer ALL=(root) NOPASSWD: /usr/local/bin/python /app/cleanup.py" >> /etc/sudoers

# Expose port
EXPOSE 5000

# Run as developer
USER developer

CMD ["python", "app.py"]
