from typing import *

import pyglet
import random
import datetime

BLOCK_SIZE = 30
ROWS = 20
COLUMNS = 10

FPS = 2


def draw_rect(x, y, color):
    pyglet.graphics.draw(4,
                         pyglet.gl.GL_QUADS,
                         ('v2i', (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                  x * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                  (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                  (x + 1) * BLOCK_SIZE, y * BLOCK_SIZE)),
                         ('c3B', color * 4))


def draw_gridline(startpoint, endpoint):
    x0, y0 = startpoint
    x1, y1 = endpoint

    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                         ('v2i', (x0, y0, x1, y1)),
                         ('c3B', (80, 80, 80) * 2))


def draw_grid():
    for x in range(1, COLUMNS + 1):
        draw_gridline((x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, BLOCK_SIZE * ROWS))

    for y in range(1, ROWS):
        draw_gridline((0, y * BLOCK_SIZE), (BLOCK_SIZE * COLUMNS, y * BLOCK_SIZE))


def write_score_to_file(name):
    with open('highscores.txt', 'a') as f:
        print(datetime.datetime.now(), name, game.rows_cleared, file=f)


class Block:
    x: int
    y: int

    squares: List[Tuple[int, int]]
    color: Tuple[int, int, int]

    def __init__(self, squares, color):
        self.squares = list(squares)
        self.color = color
        self.x, self.y = self.get_starting_position()

    def get_starting_position(self):
        ylist = [y for x, y in self.squares]
        x = COLUMNS // 2 - 1
        y = ROWS - max(ylist) - 1
        return x, y

    def rotate(self, clockwise: bool):
        # get squares after rotation
        new_squares = []

        for x, y in self.squares:
            if clockwise:
                new_squares.append((y, -x))
            else:
                new_squares.append((-y, x))

        # check if all squares are now inside
        all_inside = True
        for x, y in new_squares:
            new_x = self.x + x
            new_y = self.y + y
            if not (0 <= new_x < COLUMNS and 0 <= new_y < ROWS and not game.board[new_y][new_x]):
                all_inside = False

        # if they are inside, set as the new block
        if all_inside:
            self.squares = new_squares

    def drop(self):
        will_hit = False
        while True:
            for x, y in self.squares:
                next_y = self.y + y - 1
                next_x = self.x + x
                if next_y < 0 or game.board[next_y][next_x]:
                    will_hit = True

            game.update(0)
            if will_hit:
                break


class BlockFactory:
    blocks = [
        # O
        ((0, 0),
         (1, 0),
         (0, 1),
         (1, 1)),

        # I
        ((0, -1),
         (0, 0),
         (0, 1),
         (0, 2)),

        # L
        ((1, -1),
         (0, -1),
         (0, 0),
         (0, 1)),

        # J
        ((-1, -1),
         (0, -1),
         (0, 0),
         (0, 1)),

        # S
        ((-1, -1),
         (0, -1),
         (0, 0),
         (1, 0)),

        # Z
        ((1, -1),
         (0, -1),
         (0, 0),
         (-1, 0)),

        # T
        ((-1, 0),
         (0, 0),
         (1, 0),
         (0, 1)),
    ]

    colors = [
        # O I L J S Z T
        (255, 255, 0),
        (0, 255, 255),
        (255, 150, 0),
        (0, 0, 255),
        (255, 0, 0),
        (0, 255, 0),
        (200, 0, 200)
    ]

    def create_random_block(self):
        i = random.randint(0, 6)
        return Block(self.blocks[i], self.colors[i])


class EndScreen:
    score_label: pyglet.text.Label
    enter_name_label: pyglet.text.Label
    name_label: pyglet.text.Label

    def __init__(self, window, endscore):
        self.score_label = pyglet.text.Label(f'Score: {endscore}',
                                             x=window.width // 2,
                                             y=window.height * 0.7,
                                             anchor_x='center',
                                             anchor_y='center',
                                             font_size=20)

        self.enter_name_label = pyglet.text.Label('ENTER YOUR NAME',
                                                  x=window.width // 2,
                                                  y=window.height * 0.8,
                                                  anchor_x='center',
                                                  anchor_y='center',
                                                  font_size=20)
        self.name_label = pyglet.text.Label('',
                                            x=window.width // 2,
                                            y=window.height * 0.5,
                                            anchor_x='center',
                                            anchor_y='center',
                                            font_size=20)

    def draw(self):
        self.score_label.draw()
        self.enter_name_label.draw()
        self.name_label.draw()

    def on_key_press(self, key, mod):
        if key == pyglet.window.key.BACKSPACE:
            self.name_label.text = self.name_label.text[:-1]
        elif key == pyglet.window.key.ENTER:
            write_score_to_file(self.name_label.text)
            pyglet.app.exit()

    def on_text(self, text):
        if text.lower() in 'abcdefghijklmnopqrstuvwxyzæøå':
            self.name_label.text += text


class Game:
    block_factory: BlockFactory
    active_block: Block
    saved_block: Optional[Block]
    saved: bool
    board: List[List[Optional[Tuple[int, int, int]]]]
    rows_cleared: int
    end_screen: Optional[EndScreen]

    def __init__(self):
        self.block_factory = BlockFactory()
        self.active_block = self.block_factory.create_random_block()
        self.saved_block = self.block_factory.create_random_block()
        self.saved = False
        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.rows_cleared = 0
        self.end_screen = None

    def draw(self):
        if self.end_screen is None:
            for y, row in enumerate(self.board):
                for x, color in enumerate(row):
                    if color is not None:
                        draw_rect(x, y, color)

            for x, y in self.active_block.squares:
                draw_rect(x + self.active_block.x, y + self.active_block.y, self.active_block.color)

            if self.saved_block:
                for x, y in self.saved_block.squares:
                    draw_rect(COLUMNS + x + 3, y + 4, self.saved_block.color)

            # draw grid
            draw_grid()

        else:
            self.end_screen.draw()

    def on_key_press(self, key, mod):
        if self.end_screen:
            self.end_screen.on_key_press(key, mod)
            return

        if key == pyglet.window.key.LEFT:
            self.move_block(-1)
        elif key == pyglet.window.key.RIGHT:
            self.move_block(1)
        elif key == pyglet.window.key.UP:
            self.active_block.rotate(True)
        elif key == pyglet.window.key.DOWN:
            self.update(0)
        elif key == pyglet.window.key.SPACE:
            self.active_block.drop()
        elif key == pyglet.window.key.X:
            self.active_block.rotate(False)
        elif key == pyglet.window.key.C:
            self.save_block()

    def on_text(self, text):
        if self.end_screen:
            self.end_screen.on_text(text)

    def update(self, dt):
        hit = False
        for x, y in self.active_block.squares:
            if y + self.active_block.y - 1 < 0 or self.board[y + self.active_block.y - 1][x + self.active_block.x]:
                hit = True
                break
        if hit:
            self.place_block()
            self.active_block = self.block_factory.create_random_block()

            new_board = []
            for row in self.board:
                if not all(row):
                    new_board.append(row)

            while len(new_board) < ROWS:
                new_board.append([None for _ in range(COLUMNS)])
                self.rows_cleared += 1

            self.board = new_board
        else:
            self.active_block.y -= 1

        if any(self.board[-2]):
            self.end_game()

    def end_game(self):
        self.end_screen = EndScreen(window, self.rows_cleared)
        pyglet.clock.unschedule(self.update)

    def move_block(self, dx):
        hit = False
        for x, y in self.active_block.squares:
            square_y = self.active_block.y + y
            square_x = self.active_block.x + x + dx
            if 0 <= square_y < ROWS and 0 <= square_x < COLUMNS:
                if self.board[self.active_block.y + y][self.active_block.x + x + dx]:
                    hit = True
                    break
            else:
                hit = True
                break
        if not hit:
            self.active_block.x += dx

    def place_block(self):
        for x, y in self.active_block.squares:
            if self.active_block.y + y < len(self.board) and self.active_block.x + x < len(
                    self.board[self.active_block.y + y]):
                self.board[self.active_block.y + y][self.active_block.x + x] = self.active_block.color
        self.saved = False

    def save_block(self):
        if not self.saved:
            temp = self.saved_block
            self.saved_block = self.active_block
            self.saved_block.x, self.saved_block.y = self.saved_block.get_starting_position()
            self.active_block = temp
            self.saved = True


game = Game()

# Game window
window = pyglet.window.Window(width=BLOCK_SIZE * (COLUMNS + 7),
                              height=BLOCK_SIZE * ROWS)

pyglet.clock.schedule_interval(game.update, 1 / FPS)


# Events handlers
@window.event
def on_draw():
    window.clear()
    game.draw()


@window.event
def on_key_press(key, mod):
    game.on_key_press(key, mod)


@window.event
def on_text(text):
    game.on_text(text)


# Run the game
pyglet.app.run()
