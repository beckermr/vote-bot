import time
import os


if __name__ == "__main__":
    os.makedirs("votes", exist_ok=True)
    with open("votes/test.yaml", 'w') as fp:
        fp.write("""\
start_time: %d
duration: 10
""" % time.time()
        )
