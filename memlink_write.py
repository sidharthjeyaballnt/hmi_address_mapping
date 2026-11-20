#!/usr/bin/env python3
"""
Write a value to a Pro-face HMI Internal Device address over Memory Link.

Two modes:
  - Whole word: overwrite the entire 16-bit word with --value.
  - Single bit: set/clear one bit (0-15) within a word via --bit, using a
    safe read-modify-write so other bits in that word are left untouched.

GP-Pro EX bit addresses (format word.bit, e.g. "[#MEMLINK]000005") decode
as: first 4 digits = word address, last 2 digits = bit number. E.g.
"000005" = word 0, bit 5.

Examples:
    # Write the whole word 5 to value 2
    python3 memlink_write.py --host 192.168.1.100 --address 5 --value 2

    # Set bit 5 of word 0 to 1 (read-modify-write)
    python3 memlink_write.py --host 192.168.1.100 --address 0 --bit 5 --value 1

    # Clear bit 5 of word 0 to 0
    python3 memlink_write.py --host 192.168.1.100 --address 0 --bit 5 --value 0

    # Write 2 to each of addresses 9001, 9002, 9003 (contiguous range) in one request
    python3 memlink_write.py --host 192.168.1.100 --address 7510 --value 2 --count 1
"""
import argparse
import socket

from memlink_read import read_words, write_words, MemLinkError


def main():
    ap = argparse.ArgumentParser(description="Write a value to an HMI Internal Device address")
    ap.add_argument("--host", required=True, help="HMI IP address")
    ap.add_argument("--port", type=int, default=1024, help="TCP port (default 1024)")
    ap.add_argument("--address", type=int, required=True, help="word address, 0-9999")
    ap.add_argument("--value", type=int, required=True,
                     help="value to write (0-65535 for a whole word, or 0/1 if --bit is given)")
    ap.add_argument("--bit", type=int, default=None,
                     help="bit number 0-15 within the word; if given, only this bit is "
                          "set/cleared (safe read-modify-write), rest of the word is untouched")
    ap.add_argument("--count", type=int, default=1,
                     help="write the same --value to this many consecutive addresses starting "
                          "at --address (default 1, whole-word mode only)")
    args = ap.parse_args()

    if args.count > 1 and args.bit is not None:
        ap.error("--count cannot be combined with --bit")

    if args.bit is not None and not (0 <= args.bit <= 15):
        ap.error("--bit must be 0-15")
    if args.bit is not None and args.value not in (0, 1):
        ap.error("--value must be 0 or 1 when --bit is given")
    if args.bit is None and not (0 <= args.value <= 0xFFFF):
        ap.error("--value must be 0-65535 for a whole-word write")

    try:
        sock = socket.create_connection((args.host, args.port), timeout=10)
        sock.settimeout(10)

        if args.bit is not None:
            before = read_words(sock, args.address, 1)[0]
            if args.value:
                new_value = before | (1 << args.bit)
            else:
                new_value = before & ~(1 << args.bit)
            write_words(sock, args.address, [new_value])
            after = read_words(sock, args.address, 1)[0]
            print(f"Word {args.address} before: {before} (0b{before:016b})")
            print(f"Word {args.address} after:  {after} (0b{after:016b})")
            print(f"Bit {args.bit} is now: {(after >> args.bit) & 1}")
        else:
            before = read_words(sock, args.address, args.count)
            write_words(sock, args.address, [args.value] * args.count)
            after = read_words(sock, args.address, args.count)
            for i in range(args.count):
                print(f"Address {args.address + i} before: {before[i]}  after: {after[i]}")

        sock.close()
    except (OSError, ConnectionError, MemLinkError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
