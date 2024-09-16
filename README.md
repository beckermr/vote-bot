# vote-bot
[![tests](https://github.com/beckermr/vote-bot/actions/workflows/test.yaml/badge.svg)](https://github.com/beckermr/vote-bot/actions/workflows/test.yaml)

A github action/bot to run conda-forge-style votes.

## Usage

In your repo create a GitHub Action like this

```yaml
name: vote-bot

on:
  schedule:
    - cron: '23 15 * * *'
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

jobs:
  vote-bot:
    name: vote-bot
    runs-on: "ubuntu-latest"
    steps:
      - uses: actions/checkout@v3
      - uses: beckermr/vote-bot@main
        with:
          matrix_token: ${{ secrets.MATRIX_TOKEN }}
          matrix_room: ${{ secrets.MATRIX_ROOM }}
          matrix_home_server: "https://matrix-client.matrix.org"
          email: <email to send vote notices>
          email_password: ${{ secrets.EMAIL_PASSWORD }}
          # change these to match the email address sending your vote notices
          email_smtp_server: smtp.gmail.com
          email_smtp_port: 587
          vote_notice_email: <destination email for vote notices>
          vote_directory: votes
          vote_defaults: |
            org: conda-forge
            duration: 10
```

Each vote is a YAML file with the contents:

```yaml
org: conda-forge  # name of org holding the vote
start_time:  # unix timestamp of when vote starts
            # make via python -c "import time; print(time.time())"
duration: 10  # duration of vote in days
title: "Vote to add foo to conda-forge"  # title of vote
description: |  # description of vote
  This is a vote to add foo to conda-forge.  Please vote yes or no.
```

## Configuring Matrix

To find the Matrix API token:

1. login to your account using the element web interface
2. open the settings menu
3. navigate to the "Help & About" pane
4. Scroll to the "Advanced" section
5. Copy your API token

## Configuring Email

Email authentication is done using a username and password. If you use two-factor with gmail, 
you may need to generate an [app password](https://support.google.com/mail/answer/185833?hl=en).
