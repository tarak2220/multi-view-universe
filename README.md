# Multi View Universe — Raspberry Pi 3 + physical buttons

This project preserves the Flask image viewer and adds eight physical button inputs:
Welcome, View 1–6, and Restart. Restart returns to the Welcome screen.

## 1. Project files and image placement

```text
multi_view_universe/
├── main.py
├── requirements.txt
├── hardware_wiring.txt
├── Multi View Universe Exhibit.png   # add your own welcome image
├── templates/
│   └── index.html
└── multi view universe/
    ├── 1.jpg                         # add your six images
    ├── 2.jpg
    ├── 3.jpg
    ├── 4.jpg
    ├── 5.jpg
    └── 6.jpg
```

The original ZIP did not contain the actual exhibit images. Copy your own files into the exact locations above. The welcome image must be named `Multi View Universe Exhibit.png`; the six other files must be `1.jpg` through `6.jpg`.

## 2. Wiring safety

See `hardware_wiring.txt` for BCM and physical header pin numbers. Each momentary push button connects between its assigned GPIO and GND. The program enables internal pull-up resistors. Power off the Pi before wiring. Raspberry Pi GPIO is 3.3 V only: **never connect 5 V to a GPIO pin**.

## 3. Install and run on Raspberry Pi OS

Open a terminal in this project folder. Install Flask:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The GPIO library is often available in Raspberry Pi OS system packages. Check it:

```bash
python -c "import RPi.GPIO; print('RPi.GPIO is available')"
```

If the import fails, try installing the OS package (requires network access and an account with sudo privileges):

```bash
sudo apt update
sudo apt install python3-rpi.gpio
```

If your virtual environment cannot see the system package, recreate it with `--system-site-packages` as shown above. Then run:

```bash
python main.py
```

The browser opens on the Pi at `http://127.0.0.1:5000`. Keep the terminal open while the website runs. Stop it with Ctrl+C.

## 4. Open the site from another device on the same Wi-Fi

Find the Pi's IP address:

```bash
hostname -I
```

On the other device, open `http://PI_IP_ADDRESS:5000`, replacing `PI_IP_ADDRESS` with the address shown by the Pi.

## 5. Software-only testing on a Mac/PC

Install Flask and run `python3 main.py`. If `RPi.GPIO` is unavailable, the app prints a message and the website buttons still work. Physical GPIO buttons operate only on a compatible Raspberry Pi setup.

## Button mapping

| Action | BCM GPIO | Physical header pin |
|---|---:|---:|
| Welcome | 5 | 29 |
| View 1 | 6 | 31 |
| View 2 | 13 | 33 |
| View 3 | 16 | 36 |
| View 4 | 19 | 35 |
| View 5 | 20 | 38 |
| View 6 | 21 | 40 |
| Restart | 26 | 37 |

The mapping uses BCM numbering in code. Restart returns to Welcome. The button input uses active-low logic with an internal pull-up, and software debouncing is enabled.
