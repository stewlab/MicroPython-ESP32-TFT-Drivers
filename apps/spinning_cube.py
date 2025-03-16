import math
import time
from ili9341 import Display, color565
from machine import Pin, SPI

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

LOOKUP_TABLE_SIZE = 360  # Number of entries in lookup table
ANGLE_STEP = 2 * math.pi / LOOKUP_TABLE_SIZE  # Step per index

# Precompute sine and cosine lookup tables
SIN_LUT = [math.sin(i * ANGLE_STEP) for i in range(LOOKUP_TABLE_SIZE)]
COS_LUT = [math.cos(i * ANGLE_STEP) for i in range(LOOKUP_TABLE_SIZE)]

class CubeDemo:
    def __init__(self, display):
        self.display = display
        self.angle_index = 0
        self.zoom = 1.5  # Default zoom level
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

    def rotate_point(self, x, y, z):
        index = self.angle_index % LOOKUP_TABLE_SIZE
        cos_a = COS_LUT[index]
        sin_a = SIN_LUT[index]

        x_new = x * cos_a - z * sin_a
        z_new = x * sin_a + z * cos_a
        return x_new, y, z_new

    def project(self, x, y, z):
        distance = 4 / self.zoom  # Adjust distance based on zoom
        scale = self.cube_size / (z + distance)
        return int(self.center_x + x * scale), int(self.center_y + y * scale)

    def draw_cube(self):
        projected = [self.project(*self.rotate_point(x, y, z)) for x, y, z in self.vertices]

        for start, end in self.edges:
            self.display.draw_line(*projected[start], *projected[end], color565(255, 255, 255))

    def run(self):
        while True:
            self.display.fill_rectangle(0, 0, self.display.width, self.display.height, color565(0, 0, 0))
            self.draw_cube()
            self.angle_index = (self.angle_index + 1) % LOOKUP_TABLE_SIZE  # Increment angle safely
            time.sleep(0.01)

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
