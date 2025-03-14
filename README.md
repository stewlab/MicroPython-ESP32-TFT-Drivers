# MicroPython ESP32 TFT Drivers (ILI9341/XPT2046)

This project provides MicroPython drivers for TFT displays based on the ILI9341 controller with XPT2046 touch support. Designed for any ESP32 device running MicroPython with a 240×320 TFT display, these drivers are also compatible with ST7735 displays.

The repository includes an official MicroPython firmware binary in the `firmware/` directory for convenience. This is not a custom build, but the official release to simplify the flashing process.

## Project Structure

```
MicroPython-ESP32-TFT-Drivers/
├── drivers/
│   ├── ili9341.py
│   └── xpt2046.py
├── firmware/
│   └── ESP32_GENERIC-20241129-v1.24.1.bin
└── display_test.py
```

- **drivers/** – Contains the display and touch driver files.
- **firmware/** – Contains the official MicroPython firmware binary provided for convenience.
- **display_test.py** – A test script at the project root to verify display functionality.

## Compatibility

This has been tested on the following devices:

| Device          | Link                                                                 |
|-----------------|----------------------------------------------------------------------|
| ESP32-2432S028  | [AliExpress Listing](https://www.aliexpress.com/item/1005006470918908.html) |

## Requirements

- **Hardware:** ESP32 device with a 240×320 TFT display
- **Firmware:** MicroPython (v1.24.1 recommended or later)
- **Tools:**
  - [esptool.py](https://github.com/espressif/esptool)
  - [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)
  - *(Alternatives: [Thonny](https://thonny.org), [ampy](https://github.com/adafruit/ampy), or [rshell](https://github.com/dhylands/rshell) for file transfers)*

## Installation

### 1. Flash the MicroPython Firmware

The firmware binary is included in the repository under the `firmware/` directory for your convenience. You can flash it onto your ESP32 device using one of the following methods:

#### Using esptool.py

Replace `/dev/ttyUSB0` with your device’s port if needed:

```sh
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash 0x1000 firmware/ESP32_GENERIC-20241129-v1.24.1.bin
```

Verify the flash with:

```sh
esptool.py -p /dev/ttyUSB0 flash_id
```

#### Alternative Methods

- **mpremote:** Some users may flash firmware using mpremote's built-in flash command (refer to the [mpremote documentation](https://docs.micropython.org/en/latest/reference/mpremote.html) for details).
- **GUI Tools:** Tools like Thonny or Mu Editor offer graphical interfaces for flashing firmware on ESP32 devices.

### 2. Install mpremote

If you haven't already, install `mpremote` via pip:

```sh
pip install mpremote
```

### 3. Create the `/lib` Directory on the Device

Create the `/lib` directory using mpremote’s filesystem command:

```sh
mpremote connect /dev/ttyUSB0 fs mkdir /lib
```

This command avoids the need to enter the REPL and manually create the directory.

### 4. Copy Driver Files to the Device

Upload the driver files from the `drivers` subdirectory to the device’s `/lib` directory.

#### Using mpremote

```sh
mpremote connect /dev/ttyUSB0 cp drivers/ili9341.py :/lib/ili9341.py
mpremote connect /dev/ttyUSB0 cp drivers/xpt2046.py :/lib/xpt2046.py
```

#### Alternative Methods

- **ampy:**  
  Install ampy via pip and run:
  ```sh
  ampy --port /dev/ttyUSB0 put drivers/ili9341.py /lib/ili9341.py
  ampy --port /dev/ttyUSB0 put drivers/xpt2046.py /lib/xpt2046.py
  ```
- **rshell:**  
  With rshell, copy files like this:
  ```sh
  rshell -p /dev/ttyUSB0 cp drivers/ili9341.py /pyboard/lib/ili9341.py
  rshell -p /dev/ttyUSB0 cp drivers/xpt2046.py /pyboard/lib/xpt2046.py
  ```

### 5. Additional Filesystem Commands

You can run various filesystem commands on the device using mpremote. For example, to list the contents of the root directory:

```sh
mpremote connect /dev/ttyUSB0 fs ls /
```

Other commands include:

- **Display file contents:**  
  `mpremote connect /dev/ttyUSB0 fs cat <file>`
- **List files in a directory:**  
  `mpremote connect /dev/ttyUSB0 fs ls <dir>`
- **Copy files:**  
  `mpremote connect /dev/ttyUSB0 fs cp [-rf] <src> <dest>`
- **Remove files:**  
  `mpremote connect /dev/ttyUSB0 fs rm <file>`
- **Create directories:**  
  `mpremote connect /dev/ttyUSB0 fs mkdir <dir>`
- **Remove directories:**  
  `mpremote connect /dev/ttyUSB0 fs rmdir <dir>`
- **Create empty files:**  
  `mpremote connect /dev/ttyUSB0 fs touch <file>`
- **Calculate SHA256 checksum:**  
  `mpremote connect /dev/ttyUSB0 fs sha256sum <file>`

### 6. Run the Display Test

After uploading the drivers, test the display functionality by running the test script. You can execute the test script by using the following command from the root of this project:

```sh
mpremote connect /dev/ttyUSB0 run display_test.py
```

### 7. Erase Flash (Optional)

To erase the flash memory on your device, run:

```sh
esptool.py --port /dev/ttyUSB0 erase_flash
```

## Notes

- Adjust the serial port (`/dev/ttyUSB0`) as necessary for your system.
- Ensure you have the correct firmware binary in the `firmware/` directory.
- If you encounter issues with directory paths, verify that your device has a `/lib` directory and that files are correctly located.
- For further filesystem management, refer to the [mpremote documentation](https://docs.micropython.org/en/latest/reference/mpremote.html).

