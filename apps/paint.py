from machine import Pin, SPI, ADC, idle
import time

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

spi = SPI(1, baudrate=SPI1_BAUD_RATE, sck=Pin(SPI1_SCK_PIN), mosi=Pin(SPI1_MOSI_PIN))
display = Display(spi, dc=Pin(DISPLAY_DC_PIN), cs=Pin(DISPLAY_CS_PIN), rst=Pin(DISPLAY_RST_PIN), width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=ROTATION)

backlight = Pin(21, Pin.OUT)
backlight.on()

red_led = Pin(4, Pin.OUT)
green_led = Pin(16, Pin.OUT)
blue_led = Pin(17, Pin.OUT)

red_led.off()
green_led.off()
blue_led.off()

lightsensor = ADC(34, atten=ADC.ATTN_0DB)

touch_spi = SPI(2, baudrate=SPI2_BAUD_RATE, sck=Pin(SPI2_SCK_PIN), mosi=Pin(SPI2_MOSI_PIN), miso=Pin(SPI2_MISO_PIN))


background_color = color565(0, 0, 0)
foreground_color = color565(255, 255, 255)

class Paint:
    def __init__(self, display, touch_spi):
        self.display = display
        self.touch = Touch(touch_spi, cs=Pin(33), int_pin=Pin(36), int_handler=self.touchscreen_press)
        self.color = color565(255, 0, 0)  # Default color: Red
        self.brush_size = 5
        # self.clear_screen()
        # self.color_palette()

    def clear_screen(self):
        self.display.clear(background_color)

    def color_palette(self):
        colors = [
            color565(255, 0, 0),    # Red
            color565(0, 255, 0),    # Green
            color565(0, 0, 255),    # Blue
            color565(255, 255, 0),  # Yellow
            color565(255, 0, 255),  # Magenta
            color565(0, 255, 255),  # Cyan
            color565(0, 0, 0), # black
        ]
        x = 10
        y = 10
        size = 20
        for color in colors:
            self.display.fill_rectangle(x, y, size, size, color)
            x += size + 5

    def touchscreen_press(self, x, y):
        print("Touch at " + str(x) + "," + str(y))
        if 10 <= x <= 165 and 10 <= y <= 30: #color palette area
            colors = [
                color565(255, 0, 0),
                color565(0, 255, 0),
                color565(0, 0, 255),
                color565(255, 255, 0),
                color565(255, 0, 255),
                color565(0, 255, 255),
                color565(0,0,0)
            ]
            color_index = (x-10)//25
            if 0<= color_index < len(colors):
                # self.color = colors[color_index]
                pass
        else:
            # print("self.draw()")
            self.draw(x, y)
            pass
        pass

    def touchscreen_hold(self, x, y):
        print("Touch at " + str(x) + "," + str(y))
        self.draw(x, y)
        pass

    def draw(self, x, y):
        # self.clear_screen()
        self.display.fill_circle(self.display.width - x, y, self.brush_size, foreground_color)
        # self.display.fill_rectangle(self.display.width - x, y, self.brush_size, self.brush_size, foreground_color)
        
    def update(self):
        # (x, y) = self.touch.get_touch()
        # self.draw(x, y)

        if self.touch:
            (x, y) = self.touch.raw_touch()
            # buff = self.touch.get_touch()
            print("Buffer at " + str(x) + "," + str(y))

            # if buff is not None:
            #     # x, y = self.normalize(*buff)
            #     # print("buff " + str(buff))
            #     print("Buffer at " + str(x) + "," + str(y))
                
            #     self.draw(x, y)
        pass

    def run(self):
        pass
try:
    paint_app = Paint(display, touch_spi)
    # paint_app.run()
    # paint_app.draw()
    while True:
        # paint_app.update()
        # self.touch.get_touch()
        time.sleep_ms(1)
        # idle()
except KeyboardInterrupt:
    print("\nCtrl-C pressed. Cleaning up and exiting...")
finally:
    display.cleanup()