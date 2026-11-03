# HMI Address Mapping

Tools for reading a Pro-face HMI's internal memory over Ethernet (the
"Memory Link" protocol) from a Linux PC, detecting button presses, and
mapping other screen elements to memory addresses.

## Requirements

- Python 3 (standard library only, no pip installs needed)
- The HMI's **Memory Link** driver configured in GP-Pro EX: Device/PLC
  → Manufacturer "Digital Electronics Corporation", Series "Memory
  Link", Port "Ethernet (TCP)" — this is a protocol for an external
  host to read/write the HMI's own internal word memory (addresses
  0–9999), not for talking to an external PLC.
- The project must be **transferred and running** on the physical
  unit (not just open in the GP-Pro EX editor/simulator).
- Network access from this PC to the HMI's IP on the configured port
  (default 1024).

## Files

| File | Purpose |
|---|---|
| `memlink_read.py` | Core protocol client. Reads any word address range and prints/logs the values. |
| `button_monitor.py` | Watches for button presses in real time and classifies which of the 3 known buttons was pressed. |
| `address_mapper.py` | Diff tool for mapping *new* buttons/controls to memory addresses yourself. |
| `memory_map.csv` | A full snapshot of all 10,000 Internal Device addresses, for reference. |

## 1. Reading raw memory — `memlink_read.py`

```bash
# One-off read of 10 words starting at address 0
python3 memlink_read.py --host 192.168.1.100 --address 0 --count 10 --once

# Continuous polling every 2s, logged to CSV
python3 memlink_read.py --host 192.168.1.100 --address 0 --count 20 --interval 2 --csv hmi_log.csv
```

Options: `--port` (default 1024), `--hex` (print hex instead of
decimal). It auto-reconnects on disconnect and responds to the HMI's
keepalive ("Demand Polling") frames automatically.

## 2. Watching for button presses — `button_monitor.py`

```bash
python3 button_monitor.py --host 192.168.1.100 --csv press_events.csv
```

Prints a line like `PRESS Button 2 (addr_9236=221 addr_9237=112)`
every time a button is touched, and appends it to the CSV if given.
Runs until Ctrl+C.

This only knows about the **3 buttons already mapped** (via their
touch X-coordinate ranges, hardcoded in `BUTTON_RANGES` near the top
of the file). To add more, see the next section.

## 3. Mapping additional buttons/controls — `address_mapper.py`

The HMI doesn't expose a documented list of "what's at each address" —
you have to discover it by watching what changes when you interact
with the screen. This tool automates that by diffing full memory
snapshots.

**One button at a time:**

```bash
python3 address_mapper.py --capture-pair --host 192.168.1.100 --pause 5
```

Takes a snapshot, gives you 5 seconds to press the thing you're
mapping, takes another snapshot, and prints what changed.

**Several buttons in one run** (press them one at a time, with a gap
between each):

```bash
python3 address_mapper.py --sequence --host 192.168.1.100 --duration 60 --gap 1.5
```

Captures continuously for 60s and groups changes into separate
numbered events by time, so each button you press gets its own
isolated result instead of mixing them all together.

**Manual two-step** (useful when the trigger isn't on a fixed timer,
e.g. a fault-driven alarm):

```bash
python3 address_mapper.py --snapshot before.pkl --host 192.168.1.100
# ... go trigger the thing ...
python3 address_mapper.py --snapshot after.pkl --host 192.168.1.100
python3 address_mapper.py --diff before.pkl after.pkl
```

**Reading the output:** each changed address is labeled either:
- `BIT  bit N flipped (0->1 / 1->0)` — a single on/off flag. Good
  candidate for a dedicated per-control status bit.
- `INT  multi-bit change` — treat it as a plain numeric value
  (coordinate, counter, setpoint), not a flag.

A fixed set of addresses that are known to drift on their own with
zero touch input (free-running system counters/heartbeats) are
filtered out automatically: `8, 2035, 2036, 2038, 2052, 2053`. Use
`--show-noise` to include them if you want to double-check.

## What we've mapped so far

| Address | Meaning |
|---|---|
| 9235 | Touch event pulse: normally `1`, drops to `0` momentarily on **any** screen touch (shared across all buttons — not button-specific by itself). |
| 9236 | Touch X coordinate at the moment of the last touch. |
| 9237 | Touch Y coordinate at the moment of the last touch. |
| 9945 / 9946 | Likely screen resolution (observed 800 / 480). |
| 8, 2035, 2036, 2038, 2052, 2053 | Free-running system counters/heartbeats — ignore. |

**Button classification** (by X-coordinate, address 9236):

| Button | X range |
|---|---|
| Button 1 | 0–150 |
| Button 2 | 150–280 |
| Button 3 | 280+ |

If you map new buttons and find they report through the same
9235/9236/9237 mechanism, extend the `BUTTON_RANGES` list in
`button_monitor.py` with their coordinate range. If instead a button
shows up as its own dedicated `BIT` change at a new address, you can
watch that address directly instead.

## Known limitations

- `address_mapper.py` assumes nothing else is touched during the
  capture window besides what you're trying to map — any stray touch
  will show up in the diff too.
- A new GP-Pro EX project transfer may relocate the free-running
  "noise" addresses or the touch-coordinate addresses; re-verify with
  an idle-baseline capture after uploading a new screen.
