#!/usr/bin/env python3
"""
Live monitor for touch/button press events on the HMI, detected via
Internal Device word address 9235.

Found by differential snapshotting across the full 0-9999 Internal
Device range: addr 9235 is normally 1 and dips briefly to 0 on each
touch event (not a sustained "held" level - it pulses once per touch,
confirmed reproducible across 3 separate taps with zero false triggers
during 25s of idle baseline). Addresses 9236/9237 change at the same
moments (likely touch coordinates) and are logged for context.

Known background noise (changes with zero touch, confirmed over a 25s
idle baseline) to ignore if extending this script: 8, 2035, 2036, 2038,
2052, 2053.
"""
import argparse
import csv
import datetime
import socket
import time

from memlink_read import read_words, MemLinkError

TOUCH_ADDR = 9235
CONTEXT_ADDRS = (9236, 9237)

# addr_9236 (touch X coordinate) ranges calibrated per physical button,
# by pressing each button in isolation and recording its coordinate band.
BUTTON_RANGES = [
    ("Button 1", 0, 150),
    ("Button 2", 150, 280),
    ("Button 3", 280, 999),
]


def classify_button(x: int) -> str:
    for name, lo, hi in BUTTON_RANGES:
        if lo <= x < hi:
            return name
    return f"Unknown (x={x})"


def main():
    ap = argparse.ArgumentParser(description="Log HMI touch/press events detected at word 9235")
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=1024)
    ap.add_argument("--interval", type=float, default=0.05, help="poll interval in seconds (default 0.05)")
    ap.add_argument("--csv", help="append press events to this CSV file")
    args = ap.parse_args()

    csv_writer = None
    csv_file = None
    if args.csv:
        is_new = True
        try:
            is_new = not open(args.csv).read(1)
        except FileNotFoundError:
            pass
        csv_file = open(args.csv, "a", newline="")
        csv_writer = csv.writer(csv_file)
        if is_new:
            csv_writer.writerow(["timestamp", "button", "addr_9236", "addr_9237"])
            csv_file.flush()

    last_touch = 1
    while True:
        try:
            with socket.create_connection((args.host, args.port), timeout=10) as sock:
                sock.settimeout(10)
                print(f"Connected to {args.host}:{args.port}, watching word {TOUCH_ADDR} for press events")
                while True:
                    touch = read_words(sock, TOUCH_ADDR, 1)[0]
                    if touch == 0 and last_touch == 1:
                        ctx = read_words(sock, CONTEXT_ADDRS[0], 2)
                        button = classify_button(ctx[0])
                        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
                        print(f"{ts}  PRESS  {button}  (addr_9236={ctx[0]} addr_9237={ctx[1]})")
                        if csv_writer:
                            csv_writer.writerow([ts, button, ctx[0], ctx[1]])
                            csv_file.flush()
                    last_touch = touch
                    time.sleep(args.interval)
        except (OSError, ConnectionError, MemLinkError) as e:
            print(f"Error: {e}; reconnecting in 5s")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Stopped.")
            return


if __name__ == "__main__":
    main()
