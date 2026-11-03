#!/usr/bin/env python3
"""
Self-service tool for mapping HMI screen elements to Internal Device
addresses, by diffing full memory snapshots taken before/after an action.

Workflow to map a new button/control:
    1. python3 address_mapper.py --snapshot before.pkl --host 192.168.1.100
    2. (go press the button on the HMI)
    3. python3 address_mapper.py --snapshot after.pkl --host 192.168.1.100
    4. python3 address_mapper.py --diff before.pkl after.pkl

Or do it in one shot with a pause in between:
    python3 address_mapper.py --capture-pair --host 192.168.1.100 --pause 5

To map several buttons in a single run, press them one at a time with a
gap between each (so each press lands in its own time cluster):
    python3 address_mapper.py --sequence --host 192.168.1.100 --duration 60

Known background noise (changes with zero touch, confirmed over a 25s
idle baseline) - the --diff output flags these automatically so you can
ignore them: 8, 2035, 2036, 2038, 2052, 2053.
"""
import argparse
import pickle
import socket
import time

from memlink_read import read_words, MemLinkError

KNOWN_NOISE = {8, 2035, 2036, 2038, 2052, 2053}


def full_snapshot(sock):
    words = []
    addr = 0
    while addr <= 9999:
        n = min(500, 9999 - addr + 1)
        words.extend(read_words(sock, addr, n))
        addr += n
    return words


def take_snapshot(host, port):
    sock = socket.create_connection((host, port), timeout=10)
    sock.settimeout(10)
    try:
        return full_snapshot(sock)
    finally:
        sock.close()


def diff_snapshots(before, after, ignore_known_noise=True):
    changes = []
    for addr in range(10000):
        if before[addr] != after[addr]:
            if ignore_known_noise and addr in KNOWN_NOISE:
                continue
            changes.append((addr, before[addr], after[addr]))
    return changes


def classify_change(before, after):
    """Decide whether a word's change looks like a single bit flag flipping
    or a general integer value changing, and report which bit if it's a flag."""
    xor = before ^ after
    if xor != 0 and (xor & (xor - 1)) == 0:  # exactly one bit set
        bit = xor.bit_length() - 1
        direction = "0->1" if (after & xor) else "1->0"
        return f"BIT   bit {bit:2d} flipped ({direction})"
    return "INT   multi-bit change, treat as a numeric value (not a single flag)"


def print_diff(changes):
    if not changes:
        print("No changes found (excluding known background noise).")
        return
    print(f"{len(changes)} address(es) changed:")
    for addr, b, a in changes:
        flag = " [KNOWN NOISE]" if addr in KNOWN_NOISE else ""
        kind = classify_change(b, a)
        print(f"  address {addr:5d}: {b:6d} (0x{b:04x} = {b:016b}) -> "
              f"{a:6d} (0x{a:04x} = {a:016b})  [{kind}]{flag}")


def capture_sequence(host, port, duration):
    sock = socket.create_connection((host, port), timeout=10)
    sock.settimeout(10)
    samples = []
    t0 = time.time()
    try:
        while time.time() - t0 < duration:
            samples.append((time.time() - t0, full_snapshot(sock)))
    finally:
        sock.close()
    return samples


def find_transitions(samples, ignore_known_noise=True):
    """Return a flat list of (time, addr, old, new) for every word change
    across consecutive samples, skipping known noise addresses."""
    transitions = []
    for i in range(1, len(samples)):
        t_prev, prev = samples[i - 1]
        t_cur, cur = samples[i]
        for addr in range(10000):
            if prev[addr] != cur[addr]:
                if ignore_known_noise and addr in KNOWN_NOISE:
                    continue
                transitions.append((t_cur, addr, prev[addr], cur[addr]))
    return transitions


def cluster_events(transitions, gap_seconds=1.0):
    """Group transitions into events: a new event starts whenever the gap
    since the previous transition exceeds gap_seconds."""
    if not transitions:
        return []
    transitions = sorted(transitions, key=lambda t: t[0])
    events = [[transitions[0]]]
    for t in transitions[1:]:
        if t[0] - events[-1][-1][0] > gap_seconds:
            events.append([])
        events[-1].append(t)
    return events


def print_sequence_results(events):
    if not events:
        print("No changes found (excluding known background noise). "
              "Nothing was detected as pressed during the capture.")
        return
    print(f"{len(events)} distinct event(s) detected (in time order):\n")
    for i, ev in enumerate(events, start=1):
        t_start = ev[0][0]
        print(f"Event {i}  (~{t_start:.1f}s into capture):")
        for t, addr, b, a in ev:
            kind = classify_change(b, a)
            print(f"    address {addr:5d}: {b:6d} (0x{b:04x}) -> {a:6d} (0x{a:04x})  [{kind}]")
        print()


def main():
    ap = argparse.ArgumentParser(description="Map HMI screen elements to Internal Device addresses")
    ap.add_argument("--host", default="192.168.1.100")
    ap.add_argument("--port", type=int, default=1024)
    ap.add_argument("--snapshot", help="take a snapshot now and save it to this file")
    ap.add_argument("--diff", nargs=2, metavar=("BEFORE", "AFTER"), help="compare two saved snapshots")
    ap.add_argument("--capture-pair", action="store_true",
                     help="take a before snapshot, pause, take an after snapshot, then diff")
    ap.add_argument("--pause", type=float, default=5.0, help="seconds to pause in --capture-pair mode")
    ap.add_argument("--show-noise", action="store_true", help="include known-noisy addresses in diff output")
    ap.add_argument("--sequence", action="store_true",
                     help="continuously capture for --duration seconds, clustering changes into separate "
                          "events so you can map several buttons in one run (press them one at a time, "
                          "with a pause between each)")
    ap.add_argument("--duration", type=float, default=60.0, help="capture duration in seconds for --sequence")
    ap.add_argument("--gap", type=float, default=1.0,
                     help="minimum seconds of inactivity that separates two events in --sequence")
    args = ap.parse_args()

    try:
        if args.diff:
            with open(args.diff[0], "rb") as f:
                before = pickle.load(f)
            with open(args.diff[1], "rb") as f:
                after = pickle.load(f)
            print_diff(diff_snapshots(before, after, ignore_known_noise=not args.show_noise))
            return

        if args.sequence:
            print(f"Capturing for {args.duration}s. Press each button ONE AT A TIME, "
                  f"leaving at least {args.gap}s of no touching between presses.")
            samples = capture_sequence(args.host, args.port, args.duration)
            print(f"Captured {len(samples)} snapshots. Analyzing...\n")
            transitions = find_transitions(samples, ignore_known_noise=not args.show_noise)
            events = cluster_events(transitions, gap_seconds=args.gap)
            print_sequence_results(events)
            return

        if args.capture_pair:
            print("Taking BEFORE snapshot...")
            before = take_snapshot(args.host, args.port)
            print(f"Done. Now go perform the action on the HMI. Waiting {args.pause}s...")
            time.sleep(args.pause)
            print("Taking AFTER snapshot...")
            after = take_snapshot(args.host, args.port)
            print_diff(diff_snapshots(before, after, ignore_known_noise=not args.show_noise))
            return

        if args.snapshot:
            words = take_snapshot(args.host, args.port)
            with open(args.snapshot, "wb") as f:
                pickle.dump(words, f)
            print(f"Saved snapshot of {len(words)} words to {args.snapshot}")
            return

        ap.print_help()
    except (OSError, ConnectionError, MemLinkError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
