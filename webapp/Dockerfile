FROM python:3.12

# Install packages
RUN apt update -y

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install ssh server and run it
RUN DEBIAN_FRONTEND=noninteractive apt install openssh-server -y --fix-missing --no-install-recommends

# enable password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

RUN chmod 0755 /var/run/sshd

# Install Google Chrome

RUN python -m pip install --upgrade pip

# Disable pycache
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .

RUN chmod +x /app/entrypoint.sh

COPY user.txt /home/Andy/flag.txt

EXPOSE 80

CMD ["/app/entrypoint.sh"]