import os
import time
import yaml
import glob

ONE_DAY = 86400


def send_matrix_message(msg):
    print("Sending matrix message: %s" % msg)
    from matrix_client.api import MatrixHttpApi

    matrix = MatrixHttpApi(
        "https://matrix-client.matrix.org",
        token=os.environ["MATRIX_TOKEN"]
    )
    matrix.send_message(os.environ["MATRIX_ROOM"], msg)


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
    msg = None
    if curr_time - start_time >= 0 and curr_time - start_time <= 1.5 * ONE_DAY:
        msg = "start"
    elif curr_time - midpoint >= 0 and curr_time - midpoint <= 1.5 * ONE_DAY:
        msg = "mid"
    elif end_time - curr_time <= 1.5 * ONE_DAY and end_time >= curr_time:
        msg = "end"

    if msg is not None:
        send_matrix_message(msg)


if __name__ == "__main__":
    votes = glob.glob("votes/*.yaml")
    for vote in votes:
        config = read_config(vote)
        process_config(config)
