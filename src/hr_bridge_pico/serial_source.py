"""Finds the board's USB serial port and turns the lines it prints into readings."""

from serial.tools import list_ports

RP2_VID = 0x2E8A
MICROPYTHON_PID = 0x0005
BAUD = 115200
READ_TIMEOUT = 15
MAX_BPM = 300


def find_port(ports=None):
    """Prefers a board running MicroPython, then falls back to any Raspberry Pi USB device."""
    candidates = list(list_ports.comports() if ports is None else ports)
    for port in candidates:
        if port.vid == RP2_VID and port.pid == MICROPYTHON_PID:
            return port.device
    for port in candidates:
        if port.vid == RP2_VID:
            return port.device
    return None


def parse_line(raw):
    """Bare integers are readings. Everything else is a firmware diagnostic and is dropped."""
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("ascii", "replace")
    text = raw.strip()
    if not text.isdigit():
        return None
    bpm = int(text)
    if bpm < 1 or bpm > MAX_BPM:
        return None
    return bpm
