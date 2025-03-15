from ili9341 import Display, color565
from xpt2046 import Touch
from machine import idle, Pin, SPI
import time
import random

class Tetris:

    CYAN = color565(0, 255, 255)
    PURPLE = color565(255, 0, 255)
    WHITE = color565(255, 255, 255)

    COLORS = [color565(0, 0, 0), color565(255, 0, 0), color565(0, 255, 0),
              color565(0, 0, 255), color565(255, 255, 0), color565(0, 255, 255), color565(255, 0, 255)]

    SHAPES = [
        [(0, 0), (1, 0), (0, 1), (1, 1)],  # Square
        [(0, 0), (1, 0), (2, 0), (3, 0)],  # Line
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # L-shape
        [(2, 0), (0, 1), (1, 1), (2, 1)],  # J-shape
        [(1, 0), (0, 1), (1, 1), (2, 1)],  # T-shape
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z-shape
        [(1, 0), (2, 0), (0, 1), (1, 1)]   # S-shape
    ]

    def __init__(self, display, spi2, portrait=True):
        self.display = display
        # Reserve 40 pixels at the bottom for controls:
        self.CONTROL_HEIGHT = 40

        # Adjust block size and board height so that the board uses only the area above the controls
        self.BLOCK_SIZE = min(display.width // 10, (display.height - self.CONTROL_HEIGHT) // 20)
        self.BOARD_WIDTH = display.width // self.BLOCK_SIZE
        self.BOARD_HEIGHT = (display.height - self.CONTROL_HEIGHT) // self.BLOCK_SIZE

        self.portrait = portrait

        self.touch = Touch(spi2, cs=Pin(33), int_pin=Pin(36),
                           int_handler=self.touchscreen_press)
        self.touch_event = False
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.running = True
        self.drop_speed = 500  # milliseconds per drop
        self.last_drop_time = time.ticks_ms()

    def new_piece(self):
        shape = random.choice(self.SHAPES)
        color = random.randint(1, len(self.COLORS) - 1)
        # start roughly centered
        return {'shape': shape, 'x': self.BOARD_WIDTH // 2 - 1, 'y': 0, 'color': color}

    def transform_coordinates(self, x, y):
        # For board drawing only. Controls will be drawn using raw coordinates.
        if self.portrait:
            return y, self.display.width - x - self.BLOCK_SIZE
        return x, y

    def draw_board(self):
        # Draw only the game board area (above the control area)
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                tx, ty = self.transform_coordinates(x * self.BLOCK_SIZE, y * self.BLOCK_SIZE)
                self.display.fill_rectangle(tx, ty, self.BLOCK_SIZE, self.BLOCK_SIZE, self.COLORS[self.board[y][x]])

    def draw_piece(self, piece, clear=False):
        color = self.COLORS[0] if clear else self.COLORS[piece['color']]
        for px, py in piece['shape']:
            x, y = (piece['x'] + px) * self.BLOCK_SIZE, (piece['y'] + py) * self.BLOCK_SIZE
            tx, ty = self.transform_coordinates(x, y)
            self.display.fill_rectangle(tx, ty, self.BLOCK_SIZE, self.BLOCK_SIZE, color)

    def can_move(self, piece, dx, dy):
        for px, py in piece['shape']:
            nx, ny = piece['x'] + px + dx, piece['y'] + py + dy
            if nx < 0 or nx >= self.BOARD_WIDTH or ny >= self.BOARD_HEIGHT or (ny >= 0 and self.board[ny][nx]):
                return False
        return True

    def merge_piece(self, piece):
        for px, py in piece['shape']:
            self.board[piece['y'] + py][piece['x'] + px] = piece['color']

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = self.BOARD_HEIGHT - len(new_board)
        self.board = [[0] * self.BOARD_WIDTH for _ in range(lines_cleared)] + new_board

    def update(self):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_drop_time) >= self.drop_speed:
            if self.can_move(self.current_piece, 0, 1):
                self.draw_piece(self.current_piece, clear=True)
                self.current_piece['y'] += 1
                self.draw_piece(self.current_piece)
            else:
                self.merge_piece(self.current_piece)
                self.clear_lines()
                self.current_piece = self.new_piece()
                if not self.can_move(self.current_piece, 0, 0):
                    self.running = False
            self.last_drop_time = current_time

        # Process any pending touch events for on-screen controls
        self.handle_touch_controls()
        # Redraw control buttons on top of the board
        self.draw_controls()

    def touchscreen_press(self, pin, event):
        self.touch_event = True


    def handle_touch_controls(self):
        if self.touch_event:
            # Replace read() with the correct method, e.g., get_touch()
            point = self.touch.get_touch()  
            if point is not None:
                self.process_touch(*point)
            self.touch_event = False


    def process_touch(self, x, y):
        # Check if the touch is within the control area at the bottom of the screen.
        if y >= self.display.height - self.CONTROL_HEIGHT:
            # Divide the width into three equal regions.
            third = self.display.width // 3
            if x < third:
                # Left button: move left if possible.
                if self.can_move(self.current_piece, -1, 0):
                    self.draw_piece(self.current_piece, clear=True)
                    self.current_piece['x'] -= 1
                    self.draw_piece(self.current_piece)
            elif x < 2 * third:
                # Drop button: perform a hard drop.
                self.hard_drop()
            else:
                # Right button: move right if possible.
                if self.can_move(self.current_piece, 1, 0):
                    self.draw_piece(self.current_piece, clear=True)
                    self.current_piece['x'] += 1
                    self.draw_piece(self.current_piece)

    def hard_drop(self):
        # Clear current piece, then drop it until it collides.
        self.draw_piece(self.current_piece, clear=True)
        while self.can_move(self.current_piece, 0, 1):
            self.current_piece['y'] += 1
        self.draw_piece(self.current_piece)
        self.merge_piece(self.current_piece)
        self.clear_lines()
        self.current_piece = self.new_piece()
        if not self.can_move(self.current_piece, 0, 0):
            self.running = False
        self.last_drop_time = time.ticks_ms()

    def draw_controls(self):
        # Draw three buttons in the reserved control area.
        button_height = self.CONTROL_HEIGHT
        button_y = self.display.height - button_height
        third = self.display.width // 3

        # Use a dark gray background for the buttons.
        btn_color = color565(50, 50, 50)
        # Draw Left button.
        self.display.fill_rectangle(0, button_y, third, button_height, btn_color)
        self.display.draw_text8x8(10, button_y + button_height // 2 - 4, "LEFT", self.WHITE)
        # Draw Drop button.
        self.display.fill_rectangle(third, button_y, third, button_height, btn_color)
        self.display.draw_text8x8(third + 10, button_y + button_height // 2 - 4, "DROP", self.WHITE)
        # Draw Right button.
        self.display.fill_rectangle(2 * third, button_y, self.display.width - 2 * third, button_height, btn_color)
        self.display.draw_text8x8(2 * third + 10, button_y + button_height // 2 - 4, "RIGHT", self.WHITE)

    def show_title_screen(self):
        # Clear full display (both board and controls).
        self.display.fill_rectangle(0, 0, self.display.width, self.display.height, color565(0, 0, 0))
        self.draw_text("TETRIS", x=self.display.width // 2 - 40, y=self.display.height // 4, color=color565(255, 255, 255), size=3)
        self.draw_text("Tap to start", x=self.display.width // 2 - 70, y=self.display.height // 2 + 20, color=color565(255, 255, 255), size=2)
        while not self.touch_event:
            time.sleep(0.1)

    def draw_text(self, text, x=None, y=None, color=color565(255, 255, 255), font=None, size=2):
        if x is None:
            x = self.display.width // 2 - len(text) * 3
        if y is None:
            y = self.display.height // 2
        tx, ty = self.transform_coordinates(x, y)
        self.display.draw_text8x8(tx, ty, text, color)

def test():
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))
    bl_pin = Pin(21, Pin.OUT)
    bl_pin.on()
    spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))
    game = Tetris(display, spi2, portrait=False)

    # Initial drawing of the board.
    game.draw_board()

    while True:
        game.touch_event = False
        game.show_title_screen()
        game.reset_game()
        game.draw_board()

        try:
            while game.running:
                game.update()
                idle()
        except KeyboardInterrupt:
            print("\nCtrl-C pressed. Exiting...")
            break
        finally:
            display.cleanup()

test()
