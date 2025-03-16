from machine import Pin, SPI, SDCard, ADC, idle
import os

# https://github.com/rdagger/micropython-ili9341
from ili9341 import Display, color565
from xpt2046 import Touch

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
    
# Set up SPI for display
# Baud rate of 80000000 seems about the max
# display_spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
spi = SPI(1, baudrate=SPI1_BAUD_RATE, sck=Pin(SPI1_SCK_PIN), mosi=Pin(SPI1_MOSI_PIN))

# Set up display
# The library needs a reset pin, which does not exist on this board
# display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(15))
# display = Display(display_spi, dc=Pin(2), cs=Pin(15), rst=Pin(0))
display = Display(spi, dc=Pin(DISPLAY_DC_PIN), cs=Pin(DISPLAY_CS_PIN), rst=Pin(DISPLAY_RST_PIN), width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=ROTATION)


# Turn on display backlight
backlight = Pin(21, Pin.OUT)
backlight.on()

# Clear display to yellow
display.clear(color565(255, 255, 0))

# RGB LED at the back
red_led = Pin(4, Pin.OUT)
green_led = Pin(16, Pin.OUT)
blue_led = Pin(17, Pin.OUT)

# Turn on all LEDs (active low)
# RGB LED (and backlight) will also work with machine.PWM for dimming

red_led.off()
green_led.off()
blue_led.off()

    # spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    # display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))
    # bl_pin = Pin(21, Pin.OUT)
    # bl_pin.on()
    # spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))
    # game = Tetris(display, spi2, portrait=False)

# Set up SD card 
# sd = SDCard(slot=2, sck=Pin(18), miso=Pin(19), mosi=Pin(23), cs=Pin(5))
# # Print SD card info (seems to be card size and sector size?)
# print(sd.info())

# Mount SD card and print directory listing
# SD card must be formatted with a file system recognised by ESP32 (FAT)
# os.mount(sd, "/sd")
# print(os.listdir("/sd"))

# Read light sensor
lightsensor = ADC(34, atten=ADC.ATTN_0DB)
print(lightsensor.read_uv())



# Read touch screen
touch_spi = SPI(1, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

def touchscreen_press(x, y):
    print("Touch at " + str(x) + "," + str(y))

touch = Touch(touch_spi, cs=Pin(33), int_pin=Pin(36), int_handler=touchscreen_press)

# loop to wait for touchscreen test
try:
    while True:
        touch.get_touch()

except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Cleaning up and exiting...")
finally:
    display.cleanup()
