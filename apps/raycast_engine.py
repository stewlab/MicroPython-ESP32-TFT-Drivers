import math
import time
from ili9341 import Display, color565
from machine import Pin, SPI

# Display Configuration
DISPLAY_WIDTH = const(240)
DISPLAY_HEIGHT = const(320)
ROTATION = const(90)

# SPI Configuration
SPI1_BAUD_RATE = const(40000000)
SPI1_SCK_PIN = const(14)
SPI1_MOSI_PIN = const(13)
DISPLAY_DC_PIN = const(2)
DISPLAY_CS_PIN = const(15)
DISPLAY_RST_PIN = const(0)
BL_PIN = const(21)

# Raycasting Configuration
MAP_WIDTH = 16
MAP_HEIGHT = 16
FOV = math.pi / 3  # Field of View
PLAYER_SPEED = 0.1
ROTATION_SPEED = 0.05
WALL_HEIGHT = 64

# Map (1 = wall, 0 = empty)
map_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class Raycaster:
    def __init__(self, display):
        self.display = display
        self.player_x = 3.5
        self.player_y = 3.5
        self.player_angle = 0

    def cast_ray(self, ray_angle):
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)

        map_x = int(self.player_x)
        map_y = int(self.player_y)

        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

        step_x = 1 if ray_dir_x > 0 else -1
        step_y = 1 if ray_dir_y > 0 else -1

        side_dist_x = (map_x + 1 - self.player_x) * delta_dist_x if ray_dir_x > 0 else (self.player_x - map_x) * delta_dist_x
        side_dist_y = (map_y + 1 - self.player_y) * delta_dist_y if ray_dir_y > 0 else (self.player_y - map_y) * delta_dist_y

        hit = False
        side = 0

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                return DISPLAY_HEIGHT #return max distance if no wall is hit.
            if map_data[map_y][map_x] == 1:
                hit = True

        if side == 0:
            perp_wall_dist = (map_x - self.player_x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_dist = (map_y - self.player_y + (1 - step_y) / 2) / ray_dir_y

        return perp_wall_dist

    def render(self):
        for x in range(DISPLAY_WIDTH):
            camera_x = 2 * x / DISPLAY_WIDTH - 1
            ray_angle = self.player_angle + FOV / 2 * camera_x
            distance = self.cast_ray(ray_angle)

            line_height = int(WALL_HEIGHT / distance) if distance > 0 else DISPLAY_HEIGHT

            draw_start = max(0, int(DISPLAY_HEIGHT / 2 - line_height / 2))
            draw_end = min(DISPLAY_HEIGHT - 1, int(DISPLAY_HEIGHT / 2 + line_height / 2))

            color = color565(255, 255, 255)  # White wall for now

            for y in range(draw_start, draw_end + 1):
                self.display.draw_pixel(x, y, color)

    def update(self):
        keys = self.get_keys() #replace with your key handling.
        if keys:
            if keys[0]: #forward
                self.player_x += math.cos(self.player_angle) * PLAYER_SPEED
                self.player_y += math.sin(self.player_angle) * PLAYER_SPEED
            if keys[1]: #backward
                self.player_x -= math.cos(self.player_angle) * PLAYER_SPEED
                self.player_y -= math.sin(self.player_angle) * PLAYER_SPEED
            if keys[2]: #left
                self.player_angle += ROTATION_SPEED
            if keys[3]: #right
                self.player_angle -= ROTATION_SPEED

    def get_keys(self):
        #Replace this with your key
        pass

def main():
    spi = SPI(1, baudrate=SPI1_BAUD_RATE, sck=Pin(SPI1_SCK_PIN), mosi=Pin(SPI1_MOSI_PIN))
    display = Display(spi, dc=Pin(DISPLAY_DC_PIN), cs=Pin(DISPLAY_CS_PIN), rst=Pin(DISPLAY_RST_PIN), width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=ROTATION)
    bl_pin = Pin(BL_PIN, Pin.OUT)
    bl_pin.on()

    raycaster = Raycaster(display)

    while True:
        raycaster.update()
        # display.fill(color565(0, 0, 0)) #clear screen
        # display.fill_rectangle(0, 0, display.width, display.height, color565(0, 0, 0))
        display.clear(color565(0, 0, 0))
        raycaster.render()
        time.sleep_ms(30) #adjust to change speed.

if __name__ == "__main__":
    main()