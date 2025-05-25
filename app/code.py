NETWORK_SPEED = """
from os import geteuid, listdir
from sys import stderr, argv
from multiprocessing import Pool
from functools import partial
from time import sleep
from datetime import datetime

DEFAULT_SLEEP = 1.0


def get_total_bytes(upload: bool, interface: str) -> int:
    side = "tx" if upload else "rx"
    with open(f"/sys/class/net/{interface}/statistics/{side}_bytes") as f:
        return int(f.read().strip())


def main() -> int:
    if geteuid():
        print("permission denied.", file=stderr)
        return 1

    if len(argv) < 2:
        to_sleep = DEFAULT_SLEEP
    else:
        to_sleep = float(argv[1]) or DEFAULT_SLEEP

    interfaces = [
        interface
        for interface in listdir("/sys/class/net")
        if not any(map(lambda arg: interface.startswith(arg), argv[2:]))
    ]

    with Pool() as pool:
        before = datetime.now()
        total_tx = sum(pool.map(partial(get_total_bytes, True), interfaces))
        total_rx = sum(pool.map(partial(get_total_bytes, False), interfaces))

        sleep(to_sleep)

        elapsed = (datetime.now() - before).total_seconds()
        after_total_tx = sum(pool.map(partial(get_total_bytes, True), interfaces))
        after_total_rx = sum(pool.map(partial(get_total_bytes, False), interfaces))

    tx_diff = after_total_tx - total_tx
    rx_diff = after_total_rx - total_rx

    up_speed = f"{round(tx_diff / 1024 / elapsed, 2)} KiB/s"
    dl_speed = f"{round(rx_diff / 1024 / elapsed, 2)} KiB/s"

    print("UP:", up_speed)
    print("DL:", dl_speed)

    return 0


if __name__ == "__main__":
    exit(main())
"""