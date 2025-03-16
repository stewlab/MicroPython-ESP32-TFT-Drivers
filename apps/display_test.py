from micropython import const
from ili9341 import Display, color565
from xpt2046 import Touch
from machine import idle, Pin, SPI

# Display configuration
DISPLAY_WIDTH = const(240)
DISPLAY_HEIGHT = const(320)
ROTATION = const(270)  # Matches your working example

SPI1_BAUD_RATE = const(40000000)
SPI1_SCK_PIN = const(14)
SPI1_MOSI_PIN = const(13)
DISPLAY_DC_PIN = const(2)
DISPLAY_CS_PIN = const(15)
DISPLAY_RST_PIN = const(0)
BL_PIN = const(21)

# Touch configuration
TOUCH_BAUD_RATE = const(1000000)
TOUCH_SCK_PIN = const(25)
TOUCH_MOSI_PIN = const(32)
TOUCH_MISO_PIN = const(39)
TOUCH_CS_PIN = const(33)
TOUCH_INT_PIN = const(36)

class Demo:
    def __init__(self, display, touch):
        self.display = display
        self.touch = touch

    def touchscreen_press(self, x, y):
        print("Touch at: {},{}".format(x, y))  # Confirm touch in console
        
        # Flip Y-coordinates if necessary to match orientation
        y_flipped = (self.display.height - 1) - y

        # Clear a small rectangle before updating text (slightly larger for visibility)
        self.display.fill_rectangle(0, 0, self.display.width, 20, color565(0, 0, 0))

        # Draw touch coordinates on the screen
        self.display.draw_text8x8(10, 5, "X:{:03d} Y:{:03d}".format(x, y_flipped), color565(255, 255, 255))

def test():
    # Set up SPI for display
    spi_display = SPI(1, baudrate=SPI1_BAUD_RATE, sck=Pin(SPI1_SCK_PIN), mosi=Pin(SPI1_MOSI_PIN))
    display = Display(
        spi_display,
        dc=Pin(DISPLAY_DC_PIN),
        cs=Pin(DISPLAY_CS_PIN),
        rst=Pin(DISPLAY_RST_PIN),
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        rotation=ROTATION
    )
    
    # Turn on the backlight
    Pin(BL_PIN, Pin.OUT).on()
    
    # Clear display to black
    display.clear(color565(0, 0, 0))

    # Draw initial text on display
    display.draw_text8x8(display.width // 2 - 32, display.height // 2 - 9, "stewlab", color565(255, 255, 255))

    # Set up SPI for touch
    spi_touch = SPI(1, baudrate=TOUCH_BAUD_RATE, sck=Pin(TOUCH_SCK_PIN), mosi=Pin(TOUCH_MOSI_PIN), miso=Pin(TOUCH_MISO_PIN))
    
    # Define touch callback
    def touchscreen_press(x, y):
        demo.touchscreen_press(x, y)
    
    # Create Touch instance
    touch = Touch(spi_touch, cs=Pin(TOUCH_CS_PIN), int_pin=Pin(TOUCH_INT_PIN), int_handler=touchscreen_press)
    
    # Create Demo instance
    global demo
    demo = Demo(display, touch)
    
    # Poll for touch events
    try:
        while True:
            touch.get_touch()
            idle()
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Cleaning up and exiting...")
    finally:
        display.cleanup()

test()
