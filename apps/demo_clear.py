"""ILI9341 demo (clear)."""
from time import sleep, ticks_ms
from ili9341 import Display, color565
from machine import Pin, SPI  # type: ignore
import gc

colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "AQUA": (0, 255, 255),
    "MAROON": (128, 0, 0),
    "DARK_GREEN": (0, 128, 0),
    "NAVY": (0, 0, 128),
    "TEAL": (0, 128, 128),
    "PURPLE": (128, 0, 128),
    "ORANGE": (255, 128, 0),
    "DEEP_PINK": (255, 0, 128),
    "CYAN": (128, 255, 255),
}

# spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
# display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))
# bl_pin = Pin(21, Pin.OUT)
# bl_pin.on()
# spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

DISPLAY_WIDTH = const(240)
DISPLAY_HEIGHT = const(320)
ROTATION = const(90)

SPI1_BAUD_RATE = const(40000000)
SPI1_SCK_PIN = const(14)
SPI1_MOSI_PIN = const(13)
DISPLAY_DC_PIN = const(2)
DISPLAY_CS_PIN = const(15)
DISPLAY_RST_PIN = const(0)
BL_PIN = const(21)
SPI2_BAUD_RATE = const(1000000)
SPI2_SCK_PIN = const(25)
SPI2_MOSI_PIN = const(32)
SPI2_MISO_PIN = const(39)

def test():
    """Test code."""
    # Baud rate of 40000000 seems about the max
    spi = SPI(1, baudrate=SPI1_BAUD_RATE, sck=Pin(SPI1_SCK_PIN), mosi=Pin(SPI1_MOSI_PIN))
    display = Display(spi, dc=Pin(DISPLAY_DC_PIN), cs=Pin(DISPLAY_CS_PIN), rst=Pin(DISPLAY_RST_PIN), width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=ROTATION)

    # Calculate valid hlines parameters for display clear method
    valid_hlines = []
    for i in range(1, display.height):
        if display.height % i == 0:
            valid_hlines.append(i)
    # Ensure only 13 entries, truncate or repeat the last one
    valid_hlines = valid_hlines[:13]
    if len(valid_hlines) < 13:
        valid_hlines += [valid_hlines[-1]] * (13 - len(valid_hlines))
    # Ensure only 13 entries, truncate or repeat the last one
    valid_hlines = valid_hlines[:13]
    if len(valid_hlines) < 13:
        valid_hlines += [valid_hlines[-1]] * (13 - len(valid_hlines))

    print('Clearing to black...')
    start = ticks_ms()
    display.clear()
    end = ticks_ms()
    print(f'Display cleared in {end - start} ms.')
    sleep(2)

    print('Clearing to white...')
    start = ticks_ms()
    display.clear(color565(255, 255, 255))
    end = ticks_ms()
    print(f'Display cleared in {end - start} ms.')
    sleep(2)

    for hlines, (color, rgb) in zip(valid_hlines, colors.items()):
        gc.collect()
        print(f'Clearing display to {color}, hlines={hlines}...')
        try:
            start = ticks_ms()
            display.clear(hlines=hlines, color=color565(*rgb))
            end = ticks_ms()
            print(f'Display cleared in {end - start} ms.')
        except Exception as e:
            print(e)
        sleep(1)

    sleep(5)
    display.cleanup()


test()
