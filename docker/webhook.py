#!/bin/env python3

# 
# This file is part of the webhooktohugo project 
# (https://github.com/ben-kuhn/webhooktohugo).
# Copyright (c) 2022 Ben Kuhn.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

#
# This script starts an http listener on port 8090 that accepts webhooks
# from graylog.  The webhooks are sent from alerts that search for amateur
# radio callsigns.  Those webhooks are modified to anonymize potentially
# sensitive information (callsigns) and then append the incoming logs to
# a markdown file in a github repo.  The commit will trigger a ci/cd action
# to publish the newly updated page to a hugo site hosted on Cloudflare
# Pages.
#
# This script expects to be run in a docker container, although that
# is not a hard requirement.  For that reason several environment
# variables are used to pass potentially sensitive information to
# the script running in the container.
#

#
# The following environment variables are expected:
# SRC_IP = The IP of the graylog server or container sending the alert
# MYCALL = My callsign.  This is public but I don't want to be easily doxed either
# SUSCALL = Callsign of the ham whose activities on packet are suspicious
# GITHUB_TOKEN = A github token with file write access to the repo being updated
# REPO_NAME = Github repo containing your .md files
# POST_FILE = The path to the file you want to update relative to the repo root
#

import time
import webhook_listener
import os
import json
import github
import re

def process_post_request(request, *args, **kwargs):
    #Grab the request headers
    headers = (request.headers)
    # The body comes as a byte array of JSON so let's convert that.
    body_raw = request.body.read(int(request.headers['Content-Length'])) if int(request.headers.get('Content-Length',0)) > 0 else '{}'
    body = json.loads(body_raw.decode('utf-8'))

    # We are validating the source IP originating the alert
    if (request.method == "POST") and (str(headers["Remote-Addr"]) == str(os.environ["SRC_IP"])):
        # Sticking all the processing in a "try" block since graylog can be inconsistent in it's inclusion of the backlog field
        try:
            # Pulling the message out of the backlog, because counter-intuitively, it's not actually in the "Message" field of the alert.
            # Thanks graylog...
            messagetext = "```" + body["event"]["timestamp"] + " - " + body["backlog"][0]["message"] + "```"

        except:
            print("Alert did not include the required fields")

        # Ignore case for MYCALL and censor it
        compiledmt = re.compile(re.escape(os.environ["MYCALL"]), re.IGNORECASE)
        messagetext = str(compiledmt.sub("N0CALL", messagetext))
        # Ignore case for SYSCALL and censor it
        compiledmt = re.compile(re.escape(os.environ["SUSCALL"]), re.IGNORECASE)
        messagetext = str(compiledmt.sub("N0SUS", messagetext))

        # TODO: Queue up messages and move the Github connection to the main thread
        try:
            # Set up Github connection
            g = github.Github(os.environ["GITHUB_TOKEN"])
        except:
            print("Invalid Github Token")
        try:
            # Connect to the repo
            repo = g.get_repo(os.environ["REPO_NAME"])
        except:
            print("Error connecting to the Repo")
        try:
            # Grab the previous post
            contents = repo.get_contents(os.environ["POST_FILE"], ref="main")
            origpost = contents.decoded_content.decode()
        except:
            print("Error getting previous post")
        try:
            # Now we can append our message to our Hugo post.
            newpost = origpost + "\n\n" + messagetext

            # And commit the new post
            repo.update_file(contents.path, "Adding a message to the post", newpost, contents.sha, branch="main")
        except:
            print("Unable to publish the post.")

    return

# Start webhook listener
webhooks = webhook_listener.Listener(handlers={"POST": process_post_request})

try:
    webhooks.start()
except:
    print("Unable to start the http server.  Please veify the port is not in use elsewhere.")

# Main thread loop
while True:
    print("Still alive...")
    time.sleep(300)
