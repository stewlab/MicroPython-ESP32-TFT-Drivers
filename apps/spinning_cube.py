import math
import time
from ili9341 import Display, color565
from machine import Pin, SPI, idle

class CubeDemo:
    def __init__(self, display, spi2, portrait=True):
        self.display = display
        self.portrait = portrait
        self.angle = 0
        self.cube_size = min(display.width, display.height) // 4
        self.center_x = display.width // 2
        self.center_y = display.height // 2

        # Define cube vertices
        self.vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

    def transform_coordinates(self, x, y):
        # For portrait mode, swap coordinates and mirror X if needed.
        if self.portrait:
            return y, self.display.width - x
        return x, y

    def rotate_point(self, x, y, z, angle):
        # Rotate around the Y-axis only.
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x_new = x * cos_a - z * sin_a
        z_new = x * sin_a + z * cos_a
        return x_new, y, z_new

    def project(self, x, y, z):
        distance = 4  # A constant to avoid division by zero and simulate perspective.
        scale = self.cube_size / (z + distance)
        px = int(self.center_x + x * scale)
        py = int(self.center_y + y * scale)
        return self.transform_coordinates(px, py)

    def draw_cube(self):
        # Precompute rotated and projected vertices.
        projected = []
        for x, y, z in self.vertices:
            rx, ry, rz = self.rotate_point(x, y, z, self.angle)
            projected.append(self.project(rx, ry, rz))
        for start, end in self.edges:
            x1, y1 = projected[start]
            x2, y2 = projected[end]
            self.display.draw_line(x1, y1, x2, y2, color565(255, 255, 255))

    def clear_screen(self):
        self.display.fill_rectangle(0, 0, self.display.width, self.display.height, color565(0, 0, 0))

    def run(self):
        # Run continuously until interrupted.
        while True:
            self.clear_screen()
            self.draw_cube()
            self.angle += 0.05
            # A shorter sleep time for higher frame rate.
            time.sleep(0.01)

def test():
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))
    bl_pin = Pin(21, Pin.OUT)
    bl_pin.on()
    spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))
    cube_demo = CubeDemo(display, spi2, portrait=False)
    try:
        cube_demo.run()
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Exiting...")
    finally:
        display.cleanup()

test()
