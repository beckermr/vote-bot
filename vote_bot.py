import os
import time
import yaml
import glob
import smtplib
from email.message import EmailMessage

ONE_DAY = 86400


MSG_TEMPLATE = """\
Hello!

I am the friendly conda-forge-daemon vote bot. :)

The vote '{title}' {timing}! Please check your email for instructions.

See below for more information about this vote.

Cheers,
conda-forge-daemon vote bot

Vote/candidate information:
{blurb}
"""


def send_email_message(body, title):
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
    print("Sending matrix message: %s" % msg)
    from matrix_client.api import MatrixHttpApi

    matrix = MatrixHttpApi(
        os.environ["MATRIX_HOME_SERVER"],
        token=os.environ["MATRIX_TOKEN"]
    )
    matrix.send_message(os.environ["MATRIX_ROOM"], "@room\n\n" + msg)


def read_config(fname):
    with open(fname, 'r') as f:
        config = yaml.safe_load(f)
    return config


def process_config(config):
    start_time = config["start_time"]
    duration = config["duration"]

    end_time = start_time + duration
    midpoint = start_time + duration / 2

    curr_time = time.time()

    # get message to send
    title = None
    timing = None
    if curr_time - start_time >= 0 and curr_time - start_time <= 1.5 * ONE_DAY:
        title = "Vote started: %s" % config["title"]
        timing = "has started"
    elif curr_time - midpoint >= 0 and curr_time - midpoint <= 1.5 * ONE_DAY:
        title = "Vote half-way done: %s" % config["title"]
        timing = "is half-way done"
    elif end_time - curr_time <= 1.5 * ONE_DAY and end_time >= curr_time:
        title = "Vote ending soon: %s" % config["title"]
        timing = "will end in approximately one dat"

    if title is not None and timing is not None:
        msg = MSG_TEMPLATE.format(
            title=config["title"],
            timing=timing,
            blurb=config["blurb"]
        )
        send_matrix_message(msg)
        send_email_message(msg, title)


if __name__ == "__main__":
    votes = glob.glob(os.path.join(os.environ["VOTE_DIRECTORY"], "*.yaml"))
    for vote in votes:
        config = read_config(vote)
        process_config(config)
