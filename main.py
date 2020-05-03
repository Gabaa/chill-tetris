import datetime
import random
from typing import *

import pyglet

BLOCK_SIZE = 30
ROWS = 20
COLUMNS = 10

RIGHT_OFFSET = 7

FPS = 2

Color = Tuple[int, int, int]


def draw_rect(x, y, color):
    pyglet.graphics.draw(4,
                         pyglet.gl.GL_QUADS,
                         ('v2i', (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                  x * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                  (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                  (x + 1) * BLOCK_SIZE, y * BLOCK_SIZE)),
                         ('c3B', color * 4))


def draw_grid_line(startpoint, endpoint):
    x0, y0 = startpoint
    x1, y1 = endpoint

    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                         ('v2i', (x0, y0, x1, y1)),
                         ('c3B', (80, 80, 80) * 2))


def draw_grid():
    for x in range(1, COLUMNS + 1):
        draw_grid_line((x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, BLOCK_SIZE * ROWS))

    for y in range(1, ROWS):
        draw_grid_line((0, y * BLOCK_SIZE), (BLOCK_SIZE * COLUMNS, y * BLOCK_SIZE))


def write_score_to_file(name, score):
    with open('highscores.txt', 'a') as f:
        print(datetime.datetime.now(), name, score, file=f)


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


class Screen:
    def draw(self):
        raise NotImplementedError

    def update(self, dt):
        raise NotImplementedError

    def on_key_press(self, key, mod) -> bool:
        raise NotImplementedError

    def on_text(self, text) -> bool:
        raise NotImplementedError


class GameScreen(Screen):
    window: 'Window'
    block_factory: BlockFactory
    active_block: Block
    next_block: Block
    swap_block: Block
    swapped: bool
    board: List[List[Optional[Color]]]
    rows_cleared: int
    score_label: pyglet.text.Label

    def __init__(self, window: 'Window'):
        self.window = window
        self.block_factory = BlockFactory()
        self.active_block = self.block_factory.create_random_block()
        self.next_block = self.block_factory.create_random_block()
        self.swap_block = self.block_factory.create_random_block()
        self.swapped = False
        self.board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.rows_cleared = 0
        self.score_label = pyglet.text.Label(f'Score: {self.rows_cleared}',
                                             x=BLOCK_SIZE * (COLUMNS + (RIGHT_OFFSET / 2)),
                                             y=BLOCK_SIZE * (ROWS - 3),
                                             anchor_x='center', anchor_y='center',
                                             font_size=20)

    def draw(self):
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color is not None:
                    draw_rect(x, y, color)

        for x, y in self.active_block.squares:
            draw_rect(x + self.active_block.x, y + self.active_block.y, self.active_block.color)

        if self.swap_block:
            for x, y in self.swap_block.squares:
                draw_rect(COLUMNS + x + 3, y + 4, self.swap_block.color)

        for x, y in self.next_block.squares:
            draw_rect(COLUMNS + x + 3, y + 10, self.next_block.color)

        # draw grid
        draw_grid()

        self.score_label.draw()

    def on_key_press(self, key, mod) -> bool:
        if key == pyglet.window.key.LEFT:
            self.move_block(-1)
        elif key == pyglet.window.key.RIGHT:
            self.move_block(1)
        elif key == pyglet.window.key.UP:
            self.rotate_block(True)
        elif key == pyglet.window.key.DOWN:
            self.update(0)
        elif key == pyglet.window.key.SPACE:
            self.drop_block()
        elif key == pyglet.window.key.X:
            self.rotate_block(False)
        elif key == pyglet.window.key.C:
            self.save_block()
        elif key == pyglet.window.key.ESCAPE:
            return False
        return True

    def on_text(self, text) -> bool:
        return True

    def update(self, dt):
        hit = False
        for x, y in self.active_block.squares:
            if y + self.active_block.y - 1 < 0 or self.board[y + self.active_block.y - 1][x + self.active_block.x]:
                hit = True
                break
        if hit:
            self.place_block()
            self.active_block = self.next_block
            self.next_block = self.block_factory.create_random_block()

            new_board = []
            for row in self.board:
                if not all(row):
                    new_board.append(row)

            while len(new_board) < ROWS:
                new_board.append([None for _ in range(COLUMNS)])
                self.rows_cleared += 1

            self.update_score()

            self.board = new_board
        else:
            self.active_block.y -= 1

        if any(self.board[-2]):
            self.end_game()

    def update_score(self):
        self.score_label.text = f'Score: {self.rows_cleared}'

    def end_game(self):
        self.window.active_screen = EndScreen(window, self.rows_cleared)
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
        self.swapped = False

    def save_block(self):
        if not self.swapped:
            temp = self.swap_block
            self.swap_block = self.active_block
            self.swap_block.x, self.swap_block.y = self.swap_block.get_starting_position()
            self.active_block = temp
            self.swapped = True

    def drop_block(self):
        pyglet.clock.unschedule(self.update)

        will_hit = False
        while True:
            for x, y in self.active_block.squares:
                next_y = self.active_block.y + y - 1
                next_x = self.active_block.x + x
                if next_y < 0 or self.board[next_y][next_x]:
                    will_hit = True

            self.update(0)
            if will_hit:
                break

        pyglet.clock.schedule_interval(self.update, 1 / FPS)

    def rotate_block(self, clockwise: bool):
        # get squares after rotation
        new_squares = []

        for x, y in self.active_block.squares:
            if clockwise:
                new_squares.append((y, -x))
            else:
                new_squares.append((-y, x))

        # check if all squares are now inside
        all_inside = True
        for x, y in new_squares:
            new_x = self.active_block.x + x
            new_y = self.active_block.y + y
            if not (0 <= new_x < COLUMNS and 0 <= new_y < ROWS and not self.board[new_y][new_x]):
                all_inside = False

        # if they are inside, set as the new block
        if all_inside:
            self.active_block.squares = new_squares


class EndScreen(Screen):
    score_label: pyglet.text.Label
    enter_name_label: pyglet.text.Label
    name_label: pyglet.text.Label

    def __init__(self, window, score):
        self.score_label = pyglet.text.Label(f'Score: {score}',
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
        return True

    def update(self, dt):
        pass


class Window(pyglet.window.Window):
    active_screen: Screen

    def __init__(self):
        super().__init__(width=BLOCK_SIZE * (COLUMNS + RIGHT_OFFSET),
                         height=BLOCK_SIZE * ROWS)

        self.active_screen = GameScreen(self)

    def on_draw(self):
        self.clear()
        self.active_screen.draw()

    def on_key_press(self, key, mod):
        keep_running: bool = self.active_screen.on_key_press(key, mod)
        if not keep_running:
            self.close()

    def on_text(self, text):
        keep_running: bool = self.active_screen.on_text(text)
        if not keep_running:
            self.close()

    def run(self):
        pyglet.clock.schedule_interval(self.active_screen.update, 1 / FPS)
        pyglet.app.run()


if __name__ == '__main__':
    window = Window()
    window.run()
