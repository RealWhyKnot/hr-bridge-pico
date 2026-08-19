# hr-bridge-pico

Streams your heart rate into VRChat using a Raspberry Pi Pico W as the Bluetooth
receiver. The Pico listens to the chest strap and prints each reading over USB;
a small program on your computer forwards those readings to
[hr-osc](https://github.com/kamyu1537/hr-osc), which turns them into OSC for VRChat.

```
chest strap  --BLE-->  Pico W  --USB serial-->  hr-bridge-pico  --HTTP-->  hr-osc  --OSC-->  VRChat
```

If your computer already has Bluetooth, you do not need any of this. Use
[hr-bridge-ble](https://github.com/RealWhyKnot/hr-bridge-ble) instead; it talks to
the strap directly. This repository exists for machines with no usable Bluetooth
adapter, and for people who would rather keep the strap off their PC's radio
entirely.

## Compatibility

| | |
|---|---|
| Board | Raspberry Pi Pico W or Pico 2 W, running MicroPython 1.20 or newer |
| Strap | Anything that advertises the standard heart rate service `0x180D`: CooSpo, Polar, Garmin, Wahoo, Magene, most gym chest straps |
| Computer | Windows 10/11, macOS, or Linux |
| Python | 3.10 or newer, or none at all if you use the Windows executable |
| Consumer | hr-osc, or anything that accepts an HTTP POST holding a bare number |

The Pico is doing all the Bluetooth work, so the computer needs no Bluetooth
hardware, no drivers, and no pairing.

## What you need

- A Raspberry Pi Pico W or Pico 2 W and a USB cable that carries data.
- A Bluetooth heart rate strap.
- hr-osc installed and running, if you are sending this to VRChat.

## Setting up the Pico

**1. Flash MicroPython.**

Hold the BOOTSEL button while plugging the board in. It appears as a USB drive
called `RPI-RP2`. Download the `.uf2` for your board and drop it on that drive:

- [Pico 2 W](https://micropython.org/download/RPI_PICO2_W/)
- [Pico W](https://micropython.org/download/RPI_PICO_W/)

The board reboots on its own once the file finishes copying.

**2. Copy the firmware.**

```bash
pip install mpremote
mpremote connect auto fs cp firmware/main.py :main.py
```

`main.py` runs automatically every time the board powers up. Nothing else needs
to be installed on it; `aioble` ships inside the MicroPython build.

To pin the board to one specific strap, copy `firmware/hr_config.example.py` to
the board as `hr_config.py` with `DEVICE_NAME` set to part of the strap's
advertised name:

```bash
mpremote connect auto fs cp firmware/hr_config.example.py :hr_config.py
```

Leaving it empty means the board connects to the first heart rate strap it finds,
which is what you want unless there are several in the room.

**3. Check it works.**

```bash
mpremote connect auto
```

Wear the strap. Within a few seconds you should see lines like:

```
# found H6M 29014
# subscribed
67
68
67
```

Bare numbers are readings. Lines starting with `#` are the board telling you what
it is doing. Press Ctrl+] to disconnect.

## Setting up the computer

### Windows, no Python

Download the zip from [Releases](https://github.com/RealWhyKnot/hr-bridge-pico/releases),
unpack it anywhere, and run `hr-bridge-pico.exe`.

### macOS and Linux

```bash
pipx install https://github.com/RealWhyKnot/hr-bridge-pico/releases/latest/download/hr_bridge_pico-0.1.0-py3-none-any.whl
hr-bridge-pico
```

Or from a clone:

```bash
pip install -e .
hr-bridge-pico
```

On Linux your account needs permission to read the serial port. On most
distributions that means joining the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
```

Log out and back in for it to take effect.

### Running it

```bash
hr-bridge-pico
```

That is the whole configuration in the normal case. It finds the board, reads it,
and posts to `http://127.0.0.1:8080`. It waits patiently if the board is not
plugged in yet, and it keeps reading if hr-osc is closed, so start order does not
matter.

## Setting up hr-osc

hr-osc defaults to a different heart rate source, so it ignores the bridge until
you tell it to listen for HTTP. This is the single most common reason for a
working bridge showing nothing.

1. Open hr-osc.
2. On the **General** tab, set the service type to **HTTP**. It is on General, not
   on the HTTP tab, which only holds the port.
3. On the **HTTP** tab, confirm the port is `8080`.
4. Check that OSC is pointed at `127.0.0.1:9000`, which is where VRChat listens.

The config file is at `%APPDATA%\me.kamyu.hr-osc\data\config.json` on Windows if
you would rather edit it directly. The field is `service_type` and it must be
`"http"`.

VRChat also needs OSC switched on: in the radial menu, Options, OSC, Enabled.

## Options

```
--url URL          hr-osc HTTP receiver (default: http://127.0.0.1:8080)
--port PORT        serial port to use instead of detecting the board
--log LOG          log file path
--no-log-file      log to the console only
--quiet            do not echo the log to the console
--allow-multiple   skip the single-instance check
--version          print the version and exit
```

The log is written to `bridge.log` under your platform's data directory:

- Windows: `%LOCALAPPDATA%\hr-bridge-pico\bridge.log`
- macOS: `~/Library/Application Support/hr-bridge-pico/bridge.log`
- Linux: `~/.local/state/hr-bridge-pico/bridge.log`

## Starting it automatically

Templates for all three platforms are in `packaging/`, and in the `autostart`
folder of the release zip.

**Windows.** Copy `start-hidden.vbs` into the folder that holds
`hr-bridge-pico.exe`, or the folder that holds `.venv` if you installed from a
clone, then put a shortcut to it in the Startup folder. Press Win+R and enter
`shell:startup` to open that folder. The script works out its own location, so
you can move the folder later without breaking it.

**macOS.** Edit `dev.whyknot.hr-bridge-pico.plist` to replace `USERNAME`, then:

```bash
cp packaging/dev.whyknot.hr-bridge-pico.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/dev.whyknot.hr-bridge-pico.plist
```

**Linux.**

```bash
cp packaging/hr-bridge-pico.service ~/.config/systemd/user/
systemctl --user enable --now hr-bridge-pico
```

## When something is wrong

**Read the log first.** It records every state change: which port it opened, the
first reading it saw, and every disconnect.

**"waiting for the board".** The Pico is not plugged in, or the cable is
charge-only. Check that the board shows up as a serial device. `mpremote connect
auto` failing too means the problem is the board or cable, not this program.

**Nothing appears in hr-osc.** Confirm the log says `streaming, first bpm ...`.
If it does, the bridge is working and the problem is in hr-osc's configuration;
go back to the hr-osc section above. The bridge does not warn you when hr-osc is
closed, because that is a normal thing to happen while you are getting set up.

**The port is busy.** Only one program can hold the serial port. If you want to
run `mpremote`, stop the bridge first. This is also why the bridge refuses to
start twice.

**`ClearCommError` in the log on Windows.** The USB serial endpoint dropped, which
happens now and then. The bridge notices, waits three seconds, and reopens the
port. Nothing to do.

**`# no strap found, rescanning`.** Most straps only advertise while worn against
skin. Put it on, moisten the contacts, and give it ten seconds. A strap already
connected to a phone will not accept a second connection.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e . -r requirements-dev.txt
python -m ruff format --check .
python -m ruff check .
python -m unittest discover
```

Tests use only the standard library and never touch hardware.

Firmware changes are checked with the MicroPython compiler:

```bash
mpy-cross firmware/main.py -o /tmp/main.mpy
```

Releases are cut by pushing a `vYYYY.M.D.N` tag. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

GPL-3.0-or-later. See [LICENSE](LICENSE).
