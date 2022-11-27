# webhooktohugo

TL/DR:
A Python script that accepts a webhook as input, does some processing, and writes/commits the message to a file in a Github repo.
Once the file in Github is updated, a CI/CD script publishes the updated Hugo page.

This script was written for [this goofy little incident response project](https://staticvoid.systems/posts/2022/11/spies-on-the-ham-bands/) but is designed to be a basic framework for handling webhook alerts from any SEIM, doing processing, and sending the result via an API to another service i.e. Jira.
