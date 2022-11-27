FROM ubuntu:22.04

# Full system Update
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common locales

# Install needed packages
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python3-pip python3-github

# Update PIP
RUN yes | pip install --upgrade pip

# Install webhook_listener
RUN yes | pip install webhook_listener

# Pull in the webhook listener
COPY docker/webhook.py /webhook.py

RUN chmod +x /webhook.py

# Force Python STDOUT and STDERR to be unbuffered
ENV PYTHONUNBUFFERED=1

# Expose Ports
EXPOSE 8090

# Define default command
CMD /webhook.py