#!/usr/bin/env python3
"""
Pro-face "Memory Link" protocol client — ported from the repo-root
memlink_read.py so this ROS2 package is self-contained for colcon
build/install (it can't import a script living outside the workspace).

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
import socket
import struct

ESC = 0x1B
FS = 0x1C
CMD_READ = ord('R')
CMD_WRITE = ord('W')
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


def write_words(sock: socket.socket, address: int, values):
    if not (0 <= address <= 9999):
        raise ValueError("address must be 0-9999 (Internal Device range)")
    if not (1 <= len(values) <= 512):
        raise ValueError("1-512 values allowed per write")

    payload = bytes([ESC, CMD_WRITE]) + struct.pack('>H', address) + struct.pack('>H', len(values))
    for v in values:
        payload += struct.pack('>H', v & 0xFFFF)
    sock.sendall(build_frame(b'B', payload))

    marker, resp = handle_frame_until_read_response(sock)

    if resp == bytes([ACK]):
        return True

    if resp[:1] == bytes([NAK]):
        code = resp[1] if len(resp) > 1 else None
        desc = ERROR_CODES.get(code, "unknown error")
        raise MemLinkError(f"NAK from HMI on write: code {code:#04x} ({desc})" if code is not None
                            else "NAK from HMI on write (no error code)")

    raise MemLinkError(f"unrecognized write response: {resp!r}")
