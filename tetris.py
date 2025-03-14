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

    def __init__(self, display, spi2, mode='landscape'):
        self.display = display
        self.touch = Touch(spi2, cs=Pin(33), int_pin=Pin(36),
                           int_handler=self.touchscreen_press)

        self.mode = mode

        # Set board orientation based on mode (landscape or portrait)
        if self.mode == 'landscape':
            self.BLOCK_SIZE = min(display.width // 10, display.height // 20)
            self.BOARD_WIDTH = display.width // self.BLOCK_SIZE
            self.BOARD_HEIGHT = display.height // self.BLOCK_SIZE
        else:  # Portrait mode
            self.BLOCK_SIZE = min(display.height // 10, display.width // 20)
            self.BOARD_WIDTH = display.height // self.BLOCK_SIZE
            self.BOARD_HEIGHT = display.width // self.BLOCK_SIZE

        self.board = [[0 for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.running = True
        self.drop_speed = 500  # Milliseconds per drop
        self.last_drop_time = time.ticks_ms()

    def new_piece(self):
        shape = random.choice(self.SHAPES)
        color = random.randint(1, len(self.COLORS) - 1)
        return {'shape': shape, 'x': self.BOARD_WIDTH // 2 - 1, 'y': 0, 'color': color}

    def draw_board(self):
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                if self.board[y][x]:
                    self.display.fill_rectangle(x * self.BLOCK_SIZE, y * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE, self.COLORS[self.board[y][x]])

    def draw_piece(self, piece, clear=False):
        color = self.COLORS[0] if clear else self.COLORS[piece['color']]
        for px, py in piece['shape']:
            x, y = (piece['x'] + px) * self.BLOCK_SIZE, (piece['y'] + py) * self.BLOCK_SIZE
            self.display.fill_rectangle(x, y, self.BLOCK_SIZE, self.BLOCK_SIZE, color)

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
            self.draw_piece(self.current_piece, clear=True)
            if self.can_move(self.current_piece, 0, 1):
                self.current_piece['y'] += 1
            else:
                self.merge_piece(self.current_piece)
                self.clear_lines()
                self.current_piece = self.new_piece()
                if not self.can_move(self.current_piece, 0, 0):
                    self.running = False
            self.last_drop_time = current_time

        self.draw_board()
        self.draw_piece(self.current_piece)

    def touchscreen_press(self, x, y):
        old_x = self.current_piece['x']
        new_x = old_x

        if x < self.display.width // 2:
            if self.can_move(self.current_piece, -1, 0):
                new_x -= 1
        else:
            if self.can_move(self.current_piece, 1, 0):
                new_x += 1

        if old_x != new_x:
            for px, py in self.current_piece['shape']:
                clear_x = (old_x + px) * self.BLOCK_SIZE
                clear_y = (self.current_piece['y'] + py) * self.BLOCK_SIZE
                self.display.fill_rectangle(clear_x, clear_y, self.BLOCK_SIZE, self.BLOCK_SIZE, self.COLORS[0])

            self.current_piece['x'] = new_x
            self.draw_piece(self.current_piece)

    def show_title_screen(self):
        self.display.fill_rectangle(0, 0, self.display.width, self.display.height, color565(0, 0, 0))
        
        # Draw the title text
        self.draw_text("TETRIS", x=self.display.width // 2 - 40, y=self.display.height // 4, color=color565(255, 255, 255), size=3)
        self.draw_text("Touch to start", x=self.display.width // 2 - 70, y=self.display.height // 2 + 20, color=color565(255, 255, 255), size=2)

        # Wait for touch press
        while not self.touch.is_touched():  # Correct touch detection method
            time.sleep(0.1)

    def show_game_over_screen(self):
        self.display.fill_rectangle(0, 0, self.display.width, self.display.height, color565(0, 0, 0))
        
        # Draw the Game Over text
        self.draw_text("GAME OVER", x=self.display.width // 2 - 60, y=self.display.height // 4, color=color565(255, 0, 0), size=3)
        self.draw_text("Touch to restart", x=self.display.width // 2 - 90, y=self.display.height // 2 + 20, color=color565(255, 255, 255), size=2)
        
        # Wait for touch press
        while not self.touch.is_touched():  # Correct touch detection method
            time.sleep(0.1)

    def draw_text(self, text, x=None, y=None, color=color565(255, 255, 255), font=None, size=2):

        if x is None:
            x = self.display.width // 2 - len(text) * 3  # Approximate centering
        if y is None:
            y = self.display.height // 2  # Center vertically
    
        # self.display.draw_text8x8(self.display.width // 2 - 32,
        #                         self.display.height - 9,
        #                         text,
        #                         self.CYAN)
        self.display.draw_text8x8(x,y,
                        text,
                        self.CYAN)




def test():
    spi1 = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi1, dc=Pin(2), cs=Pin(15), rst=Pin(0))

    bl_pin = Pin(21, Pin.OUT)
    bl_pin.on()

    spi2 = SPI(2, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

    game = Tetris(display, spi2, mode='landscape')  # You can switch to 'portrait' mode

    game.show_title_screen()  # Show the title screen

    try:
        while game.running:
            game.update()
            if not game.running:
                game.show_game_over_screen()  # Show the game over screen
                game = Tetris(display, spi2, mode='landscape')  # Restart the game
            idle()

    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Exiting...")
    finally:
        display.cleanup()

test()
