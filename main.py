from typing import *

import pyglet
import random

BLOCK_SIZE = 30
ROWS = 20
COLUMNS = 10

FPS = 2


class Game:
    def __init__(self):
        self.block = None
        self.board = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.set_random_block_as_active()

    def update(self, dt):
        if any(self.board[-2]):
            window.close()

        hit = False
        for x, y in self.block.squares:
            if y + self.block.y - 1 < 0 or self.board[y + self.block.y - 1][x + self.block.x]:
                hit = True
                break
        if hit:
            self.place_block()
            self.set_random_block_as_active()

            new_board = []
            for row in self.board:
                if not all(row):
                    new_board.append(row)

            while len(new_board) < ROWS:
                new_board.append([False for _ in range(COLUMNS)])

            self.board = new_board
        else:
            self.block.y -= 1

    def move_block(self, dx):
        hit = False
        for x, y in self.block.squares:
            square_y = self.block.y + y
            square_x = self.block.x + x + dx
            if 0 <= square_y < ROWS and 0 <= square_x < COLUMNS:
                if self.board[self.block.y + y][self.block.x + x + dx]:
                    hit = True
                    break
            else:
                hit = True
                break
        if not hit:
            self.block.x += dx

    def place_block(self):
        for x, y in self.block.squares:
            if self.block.y + y < len(self.board) and self.block.x + x < len(self.board[self.block.y + y]):
                self.board[self.block.y + y][self.block.x + x] = True

    def set_random_block_as_active(self):
        self.block = Block(*random.choice(blocks))


class Block:
    x: int
    y: int
    squares: List[Tuple[int, int]]

    def __init__(self, *squares):
        self.squares = list(squares)

        ylist = [y for x, y in self.squares]

        self.x = COLUMNS // 2 - 1
        self.y = ROWS - max(ylist) - 1

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
game = Game()

# Game window
window = pyglet.window.Window(
    width=BLOCK_SIZE * COLUMNS,
    height=BLOCK_SIZE * ROWS
)

pyglet.clock.schedule_interval(game.update, 1 / FPS)


# Events handlers
@window.event
def on_draw():
    window.clear()
    for y, row in enumerate(game.board):
        for x, block in enumerate(row):
            if block:
                pyglet.graphics.draw(4,
                                     pyglet.gl.GL_QUADS,
                                     ('v2i', (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                              x * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                              (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                              (x + 1) * BLOCK_SIZE, y * BLOCK_SIZE)))

    for x, y in game.block.squares:
        block_left = (x + game.block.x) * BLOCK_SIZE
        block_right = block_left + BLOCK_SIZE
        block_top = (y + game.block.y) * BLOCK_SIZE
        block_bottom = block_top + BLOCK_SIZE
        pyglet.graphics.draw(4,
                             pyglet.gl.GL_QUADS,
                             ('v2i', (block_left, block_top,
                                      block_left, block_bottom,
                                      block_right, block_bottom,
                                      block_right, block_top)))


@window.event
def on_key_press(key, mod):
    if key == pyglet.window.key.LEFT:
        game.move_block(-1)
    elif key == pyglet.window.key.RIGHT:
        game.move_block(1)
    elif key == pyglet.window.key.UP:
        game.block.rotate(True)
    elif key == pyglet.window.key.DOWN:
        game.update(0)
    elif key == pyglet.window.key.SPACE:
        game.block.drop()
    elif key == pyglet.window.key.X:
        game.block.rotate(False)
    elif key == pyglet.window.key.C:
        game.block.rotate(True)


# Run the game
pyglet.app.run()
