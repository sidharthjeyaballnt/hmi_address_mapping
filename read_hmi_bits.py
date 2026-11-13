#!/usr/bin/env python3
"""Read bit (coil) values from a Pro-face HMI over Modbus TCP (no dependencies).

Modbus address 000001 -> protocol offset 0, 000002 -> 1, 000003 -> 2.
Usage: python3 read_hmi_bits.py 192.168.0.10 [--port 502] [--unit 1] [--start 1] [--count 3] [--watch]
"""
import argparse
import socket
import struct
import time


def read_coils(sock, unit, start, count, tid):
    # MBAP header + PDU (FC 01: read coils); start is the 1-based 0xxxxx address
    req = struct.pack(">HHHBBHH", tid, 0, 6, unit, 0x01, start - 1, count)
    sock.sendall(req)
    hdr = recv_exact(sock, 7)
    _, _, length, _ = struct.unpack(">HHHB", hdr)
    pdu = recv_exact(sock, length - 1)
    if pdu[0] & 0x80:
        raise RuntimeError(f"Modbus exception code {pdu[1]}")
    data = pdu[2:2 + pdu[1]]
    return [bool(data[i // 8] >> (i % 8) & 1) for i in range(count)]


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed by HMI")
        buf += chunk
    return buf


def main():
    p = argparse.ArgumentParser()
    p.add_argument("host", help="HMI IP address")
    p.add_argument("--port", type=int, default=502)
    p.add_argument("--unit", type=int, default=1)
    p.add_argument("--start", type=int, default=1, help="first bit address (1 = 000001)")
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--watch", action="store_true", help="poll continuously")
    a = p.parse_args()

    with socket.create_connection((a.host, a.port), timeout=3) as s:
        tid = 0
        while True:
            tid = (tid + 1) & 0xFFFF
            bits = read_coils(s, a.unit, a.start, a.count, tid)
            print("  ".join(f"{a.start + i:06d}={int(b)}" for i, b in enumerate(bits)))
            if not a.watch:
                break
            time.sleep(0.5)


if __name__ == "__main__":
    main()
