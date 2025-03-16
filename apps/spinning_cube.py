import math
import time
from ili9341 import Display, color565
from machine import Pin, SPI, mem32

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

class CubeDemo:
    def __init__(self, display):
        self.display = display
        self.angle = 0
        self.zoom = 1.0
        self.cube_size = min(display.width, display.height) // 4
        self.center_x = display.width // 2
        self.center_y = display.height // 2

        self.vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        self.projected = [(0, 0)] * 8  # Pre-allocate projected points

    def rotate_point(self, x, y, z, cos_a, sin_a):
        x_new = x * cos_a - z * sin_a
        z_new = x * sin_a + z * cos_a
        return x_new, y, z_new

    def project(self, x, y, z):
        distance = 4 / self.zoom
        scale = self.cube_size / (z + distance)
        return int(self.center_x + x * scale), int(self.center_y + y * scale)

    def draw_cube(self):
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        for i, (x, y, z) in enumerate(self.vertices):
            self.projected[i] = self.project(*self.rotate_point(x, y, z, cos_a, sin_a))

        for start, end in self.edges:
            self.display.draw_line(*self.projected[start], *self.projected[end], color565(255, 255, 255))

    def run(self):
        while True:
            self.display.fill_rectangle(0, 0, self.display.width, self.display.height, color565(0, 0, 0))
            self.draw_cube()
            self.angle += 0.05
            time.sleep_ms(10)

def test():
    spi = SPI(1, baudrate=SPI1_BAUD_RATE, sck=Pin(SPI1_SCK_PIN), mosi=Pin(SPI1_MOSI_PIN))
    display = Display(spi, dc=Pin(DISPLAY_DC_PIN), cs=Pin(DISPLAY_CS_PIN), rst=Pin(DISPLAY_RST_PIN), width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=ROTATION)
    bl_pin = Pin(BL_PIN, Pin.OUT)
    bl_pin.on()

    cube_demo = CubeDemo(display)

    try:
        cube_demo.run()
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Exiting...")
    finally:
        display.cleanup()

test()