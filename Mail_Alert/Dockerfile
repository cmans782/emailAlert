FROM ubuntu

RUN apt update && \
    apt-get install -y python3-pip && \ 
    apt-get install -y python3-dev && \
    apt install -y python3-venv && \
    apt install -y nginx

# removes nginx default config file
RUN rm /etc/nginx/sites-enabled/default
# copy config file into image
COPY conf /etc/nginx/sites-enabled/MailAlert

# this sets the default directory where the applicaton will be installed
# the default directory applies to any remaining commands
WORKDIR /app

# using the . because I am in the same directory as the Dockerfile
# copy the source code from my application to the image I am making
COPY . /app

RUN python3 -m venv flask_env
RUN flask_env/bin/pip install wheel
RUN flask_env/bin/pip3 install wheel

RUN flask_env/bin/pip install -r requirements.txt

COPY /etc/MailAlert_config.json /etc/

ENV FLASK_APP run.py