FROM ubuntu:22.04

# Full system Update
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common locales

# Install needed packages
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install supervisor cron python3 python3-pip

# Update PIP
RUN yes | pip install --upgrade pip

# Install webhook_listener
RUN yes | pip install webhook_listener

# Pull in the webhook listener
COPY docker/webhook.py /webhook.py

# Define default command
CMD python3 /webhook.py

# Expose Ports
Expose 8090
