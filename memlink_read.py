#!/usr/bin/env python3
"""
Reader for Pro-face "Memory Link" protocol over Ethernet (TCP).

Implements the LAN frame format from the Memory Link Driver manual
(dig_mtm.pdf), section 11:
  - 11.1  Basic frame: 'B'/'b' + 3 control bytes + 4-byte big-endian
          data length + data block.
  - 11.2  Demand Polling keepalive (display -> host "Demand Polling",
          host replies "Polling Command", display replies "Polling
          Response").
  - 11.4.1 Read command: ESC 'R' + address(2B BE) + count(2B BE) ->
          ESC 'A' + count * 2-byte words (BE), or NAK + error code.
  - 7     Only device exposed by this driver is "Internal Device"
          (the HMI's internal/USR word area), word address 0-9999.
"""
import argparse
import csv
import datetime
import socket
import struct
import sys
import time

ESC = 0x1B
FS = 0x1C
CMD_READ = ord('R')
RESP_ACK_DATA = ord('A')
ACK = 0x06
NAK = 0x15

DEMAND_POLLING = b'Demand Polling'
POLLING_COMMAND = b'Polling Command'
POLLING_RESPONSE = b'Polling Response'

ERROR_CODES = {
    0x06: "Checksum does not match",
    0x10: "Undefined code received",
    0x12: "Number of data elements does not match",
    0x15: "Display attribute out of range",
    0x16: "Character size out of range",
    0x17: "Coordinate out of range",
    0x18: "Line type out of range",
    0x19: "Tiling pattern out of range",
    0x1A: "Radius out of range",
    0x1B: "Start/end angle out of range",
    0x1C: "Character type out of range",
    0x1D: "Rotation out of range",
    0x1E: "Direction out of range",
    0x1F: "Highlighting out of range",
    0x20: "Arrow pattern out of range",
    0x21: "Arrow direction out of range",
    0x22: "Beveling method out of range",
    0x23: "Centering out of range",
    0x24: "Attribute code out of range",
    0x25: "Contrast command sent to unsupported model",
    0x26: "Contrast setting out of range",
    0x27: "Brightness command sent to unsupported model",
    0x28: "Brightness setting out of range",
    0x29: "Banner message not set",
    0x2A: "Font code out of range",
    0x2B: "Priority code out of range",
    0xFA: "Address in system area out of permissible range",
    0xFB: "Attempt to read/write outside system area",
    0xFC: "Improperly formatted data block received",
    0xFF: "Display could not send data for longer than 10 seconds",
}


class MemLinkError(Exception):
    pass


def build_frame(marker: bytes, payload: bytes) -> bytes:
    return marker + b'\x00\x00\x00' + struct.pack('>I', len(payload)) + payload


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed by HMI")
        buf += chunk
    return bytes(buf)


def recv_frame(sock: socket.socket):
    header = recv_exact(sock, 8)
    marker = header[0:1]
    if marker not in (b'B', b'b'):
        raise MemLinkError(f"unexpected frame marker {header[0]:#x}")
    data_len = struct.unpack('>I', header[4:8])[0]
    payload = recv_exact(sock, data_len) if data_len else b''
    return marker, payload


def send_polling_command(sock: socket.socket):
    sock.sendall(build_frame(b'B', bytes([FS]) + POLLING_COMMAND + b'\x00'))


def handle_frame_until_read_response(sock: socket.socket):
    """Read frames, transparently answering Demand Polling keepalives,
    until a frame that isn't a polling exchange arrives."""
    while True:
        marker, payload = recv_frame(sock)
        if marker == b'b' and payload[:1] == bytes([FS]) and DEMAND_POLLING in payload:
            send_polling_command(sock)
            continue
        if marker == b'b' and payload[:1] == bytes([FS]) and POLLING_RESPONSE in payload:
            continue
        return marker, payload


def read_words(sock: socket.socket, address: int, count: int):
    if not (0 <= address <= 9999):
        raise ValueError("address must be 0-9999 (Internal Device range)")
    if not (1 <= count <= 512):
        raise ValueError("count must be 1-512 words per request")

    payload = bytes([ESC, CMD_READ]) + struct.pack('>H', address) + struct.pack('>H', count)
    sock.sendall(build_frame(b'B', payload))

    marker, resp = handle_frame_until_read_response(sock)

    if resp[:2] == bytes([ESC, RESP_ACK_DATA]):
        data = resp[2:]
        if len(data) != count * 2:
            raise MemLinkError(
                f"expected {count * 2} data bytes, got {len(data)}"
            )
        return list(struct.unpack(f'>{count}H', data))

    if resp[:1] == bytes([NAK]):
        code = resp[1] if len(resp) > 1 else None
        desc = ERROR_CODES.get(code, "unknown error")
        raise MemLinkError(f"NAK from HMI: code {code:#04x} ({desc})" if code is not None
                            else "NAK from HMI (no error code)")

    raise MemLinkError(f"unrecognized response frame: {resp!r}")


def main():
    ap = argparse.ArgumentParser(description="Poll Pro-face Memory Link Internal Device (USR) words over Ethernet")
    ap.add_argument("--host", required=True, help="HMI IP address")
    ap.add_argument("--port", type=int, default=1024, help="TCP port (default 1024, matches GP-Pro EX setting)")
    ap.add_argument("--address", type=int, default=0, help="starting word address, 0-9999 (default 0)")
    ap.add_argument("--count", type=int, default=10, help="number of words to read, 1-512 (default 10)")
    ap.add_argument("--interval", type=float, default=2.0, help="seconds between reads (default 2.0)")
    ap.add_argument("--once", action="store_true", help="read once and exit instead of polling")
    ap.add_argument("--csv", help="append timestamped rows to this CSV file")
    ap.add_argument("--hex", action="store_true", help="print word values in hex instead of decimal")
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
            csv_writer.writerow(["timestamp"] + [f"addr_{args.address + i}" for i in range(args.count)])

    while True:
        try:
            with socket.create_connection((args.host, args.port), timeout=10) as sock:
                sock.settimeout(30)
                print(f"Connected to {args.host}:{args.port}", file=sys.stderr)
                while True:
                    words = read_words(sock, args.address, args.count)
                    ts = datetime.datetime.now().isoformat(timespec="seconds")
                    formatted = [f"{w:#06x}" if args.hex else str(w) for w in words]
                    print(f"{ts}  addr {args.address}-{args.address + args.count - 1}: {formatted}")
                    if csv_writer:
                        csv_writer.writerow([ts] + words)
                        csv_file.flush()
                    if args.once:
                        return
                    time.sleep(args.interval)
        except (OSError, ConnectionError, MemLinkError) as e:
            print(f"Error: {e}; reconnecting in 5s", file=sys.stderr)
            time.sleep(5)
        except KeyboardInterrupt:
            print("Stopped.", file=sys.stderr)
            return


if __name__ == "__main__":
    main()
