from typing import *

import pyglet
import random

BLOCK_SIZE = 30
ROWS = 20
COLUMNS = 10

FPS = 2


def update(dt):
    global active_block, board

    if any(board[-1]):
        window.close()

    hit = False
    for x, y in active_block.squares:
        if y + active_block.y - 1 < 0 or board[y + active_block.y - 1][x + active_block.x]:
            hit = True
            break
    if hit:
        active_block.place(board)
        active_block = Block(*random.choice(blocks))

        new_board = []
        for row in board:
            if not all(row):
                new_board.append(row)

        while len(new_board) < ROWS:
            new_board.append([False for _ in range(COLUMNS)])

        board = new_board
    else:
        active_block.y -= 1


class Block:
    x: int
    y: int
    squares: List[Tuple[int, int]]

    def __init__(self, *squares):
        self.squares = list(squares)

        ylist = [y for x, y in self.squares]

        self.x = COLUMNS // 2 - 1
        self.y = ROWS - max(ylist) - 1

    def move(self, board, dx):
        hit = False
        for x, y in self.squares:
            square_y = self.y + y
            square_x = self.x + x + dx
            if 0 <= square_y < ROWS and 0 <= square_x < COLUMNS:
                if board[self.y + y][self.x + x + dx]:
                    hit = True
                    break
            else:
                hit = True
                break
        if not hit:
            self.x += dx

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
            if not (0 <= new_x < COLUMNS and 0 <= new_y < ROWS and not board[new_y][new_x]):
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
                if next_y < 0 or board[next_y][next_x]:
                    will_hit = True
            
            update(0)
            if will_hit:
                break
        update(0)

    def place(self, board):
        for x, y in self.squares:
            if self.y + y < len(board) and self.x + x < len(board[self.y + y]):
                board[self.y + y][self.x + x] = True


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

active_block = Block(*random.choice(blocks))

# Game board - initially a List[List[bool]] filled with False
board = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]

# Game window
window = pyglet.window.Window(
    width=BLOCK_SIZE * COLUMNS,
    height=BLOCK_SIZE * ROWS
)

pyglet.clock.schedule_interval(update, 1 / FPS)


# Events
@window.event
def on_draw():
    window.clear()
    for y, row in enumerate(board):
        for x, block in enumerate(row):
            if block:
                pyglet.graphics.draw(4,
                                     pyglet.gl.GL_QUADS,
                                     ('v2i', (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                              x * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                              (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                                              (x + 1) * BLOCK_SIZE, y * BLOCK_SIZE)))

    for x, y in active_block.squares:
        pyglet.graphics.draw(4,
                             pyglet.gl.GL_QUADS,
                             ('v2i', ((x + active_block.x) * BLOCK_SIZE, (y + active_block.y) * BLOCK_SIZE,
                                      (x + active_block.x) * BLOCK_SIZE, (y + active_block.y + 1) * BLOCK_SIZE,
                                      (x + active_block.x + 1) * BLOCK_SIZE, (y + active_block.y + 1) * BLOCK_SIZE,
                                      (x + active_block.x + 1) * BLOCK_SIZE, (y + active_block.y) * BLOCK_SIZE)))


@window.event
def on_key_press(key, mod):
    if key == pyglet.window.key.LEFT:
        active_block.move(board, -1)
    elif key == pyglet.window.key.RIGHT:
        active_block.move(board, 1)
    elif key == pyglet.window.key.UP:
        active_block.rotate(True)
    elif key == pyglet.window.key.DOWN:
        update(0)
    elif key == pyglet.window.key.SPACE:
        active_block.drop()
    elif key == pyglet.window.key.X:
        active_block.rotate(False)
    elif key == pyglet.window.key.C:
        active_block.rotate(True)


# Run the game
pyglet.app.run()
