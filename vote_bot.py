import os
import time
import sys
import yaml
import glob
import copy
import smtplib
import textwrap
from email.message import EmailMessage

ONE_DAY = 86400


MSG_TEMPLATE = """\
Hello{salutation}!

I am the friendly conda vote bot. :)

The vote '{title}' {timing}! Please check your email for instructions.

See below for more information about this vote.

Cheers,
conda vote bot

vote details:
{details}
"""


def send_email_message(body, title):
    print(
        """\
sending email message:
    from: %s
    to: %s
    subject: %s
    content:
%s
""" % (
            os.environ["EMAIL"],
            os.environ["VOTE_NOTICE_EMAIL"],
            title,
            textwrap.indent(body, "        "),
        ),
        flush=True,
    )
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = title
    msg['From'] = os.environ["EMAIL"]
    msg['To'] = os.environ["VOTE_NOTICE_EMAIL"]

    s = smtplib.SMTP(
        os.environ["EMAIL_SMTP_SERVER"],
        int(os.environ["EMAIL_SMTP_PORT"]),
    )
    s.starttls()
    s.login(os.environ["EMAIL"], os.environ["EMAIL_PASSWORD"])
    s.send_message(msg)
    s.quit()


def send_matrix_message(msg):
    print(
        "sending matrix message:\n%s" % textwrap.indent(msg, "    "),
        flush=True,
    )
    from matrix_client.client import MatrixClient
    client = MatrixClient(os.environ["MATRIX_HOME_SERVER"])
    token = client.login(
        username=os.environ["MATRIX_USERNAME"],
        password=os.environ["MATRIX_PASSWORD"],
    )
    if (
        "GITHUB_ACTIONS" in os.environ
        and os.environ["GITHUB_ACTIONS"] == "true"
    ):
        sys.stdout.flush()
        print(f"::add-mask::{token}", flush=True)

    client.api.send_message(
        os.environ["MATRIX_ROOM_ID"],
        msg,
    )


def read_config(fname):
    with open(fname, 'r') as f:
        config = yaml.safe_load(f)
    return config


def process_config(config):
    start_time = config["start_time"]
    duration = int(config["duration"] * ONE_DAY)

    end_time = start_time + duration
    midpoint = start_time + duration / 2

    curr_time = time.time()

    org = config.get("org", "")
    if org != "":
        org = org + " "

    # get message to send
    title = None
    timing = None
    if curr_time - start_time >= 0 and curr_time - start_time <= 1.5 * ONE_DAY:
        title = "%svote started: %s" % (org, config["title"])
        timing = "has started"
    elif curr_time - midpoint >= 0 and curr_time - midpoint <= 1.5 * ONE_DAY:
        title = "%svote half-way done: %s" % (org, config["title"])
        timing = "is half-way done"
    elif end_time - curr_time <= 1.5 * ONE_DAY and end_time >= curr_time:
        title = "%svote ending soon: %s" % (org, config["title"])
        timing = "will end in approximately one day"

    if title is not None and timing is not None:
        msg = MSG_TEMPLATE.format(
            salutation=" @room",
            title=config["title"],
            timing=timing,
            details=config["details"],
        )
        send_matrix_message(msg)
        msg = MSG_TEMPLATE.format(
            salutation="",
            title=config["title"],
            timing=timing,
            details=config["details"],
        )
        send_email_message(msg, title)


if __name__ == "__main__":
    votes = glob.glob(os.path.join(os.environ["VOTE_DIRECTORY"], "*.yaml"))

    if "VOTE_DEFAULTS" in os.environ:
        default_config = yaml.safe_load(os.environ["VOTE_DEFAULTS"])

    for vote in votes:
        if os.path.basename(vote) != "defaults.yaml":
            config = read_config(vote)
            _config = copy.deepcopy(default_config)
            _config.update(config)
            print(
                "processing vote in file %s:\n%s" % (
                    vote,
                    textwrap.indent(
                        yaml.dump(_config, default_flow_style=False, indent=2),
                        "    ",
                    ),
                ),
                flush=True,
            )
            process_config(_config)
