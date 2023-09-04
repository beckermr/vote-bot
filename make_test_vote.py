import time
import os


if __name__ == "__main__":
    os.makedirs("votes", exist_ok=True)
    with open("votes/test.yaml", 'w') as fp:
        fp.write("""\
title: Matt for conda-forge Bot Master
start_time: %d
duration: 10
""" % time.time()
        )
