from __future__ import annotations

import pygame as pg
import random
from enum import Enum
import sys


class Position:
    x: int
    y: int

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other: Position):
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Position):
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int):
        return Position(self.x * other, self.y * other)

    def __str__(self):
        return f'<x: {self.x} y: {self.y}>'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Direction(Enum):
    N = Position(0, 0)
    U = Position(0, -1)
    D = Position(0, 1)
    L = Position(-1, 0)
    R = Position(1, 0)


class Segment:
    def __init__(self, color: pg.Color, position: Position, direction: Direction, head: bool = False):
        self.color = color
        self.position = position
        self.direction = direction
        self.head = head

    def set_direction(self, direction: Direction):
        self.direction = direction

    def draw(self):
        pg.draw.circle(screen, pg.Color('black'),
                       Cell.get_cell_center(self.position.x, self.position.y), CELL_WIDTH / 2)
        pg.draw.circle(screen, self.color, Cell.get_cell_center(self.position.x, self.position.y), CELL_WIDTH / 2 - 2)


class Snake:
    head: Segment
    body: list[Segment]

    @staticmethod
    def rand_color() -> pg.Color:
        color = random.choice(PALETTE)
        return pg.Color(color)

    def __init__(self, x, y):
        self.head = Segment(self.rand_color(), Position(x, y), Direction.N, True)
        self.body = list()

    def grow(self):
        last_segment = self.body[-1] if self.body else self.head
        direction = last_segment.direction
        position = last_segment.position - direction.value
        new_segment = Segment(self.rand_color(), position, direction)
        self.body.append(new_segment)

    def update_direction(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].direction = self.body[i - 1].direction
        if self.body:
            self.body[0].direction = self.head.direction

    def update_position(self):
        self.head.position += self.head.direction.value
        for seg in self.body:
            seg.position += seg.direction.value

    def change_direction(self, direction: Direction):
        self.head.direction = direction

    def draw(self):
        self.head.draw()
        for segment in self.body:
            segment.draw()


class Apple:
    def __init__(self, position: Position):
        self.position = position

    def move(self, new_position: Position):
        self.position = new_position

    def draw(self):
        pg.draw.circle(screen, pg.Color('red'), Cell.get_cell_center(self.position.x, self.position.y), CELL_WIDTH / 2)


class Cell(Enum):
    @staticmethod
    def get_cell_pos(row: int, col: int):
        return row * CELL_WIDTH, col * CELL_WIDTH

    @staticmethod
    def get_cell_center(row: int, col: int):
        return row * CELL_WIDTH + CELL_WIDTH / 2, col * CELL_WIDTH + CELL_WIDTH / 2


class Board:
    height: int
    width: int
    cell_width: int
    background_color: pg.Color
    score: int
    apple: Apple
    snake: Snake

    def __init__(self, cell_width: int, width: int, height: int, background_color):
        self.height = height
        self.width = width
        self.cell_width = cell_width
        self.background_color = background_color
        self.set_board()

    def check_snake_collision(self):
        head_pos = self.snake.head.position
        if head_pos.x < 0 or head_pos.y < 0 or head_pos.x >= self.width or head_pos.y >= self.height:
            return True
        body = self.snake.body
        for i in range(len(body)):
            if body[i].position == head_pos:
                return True
            for j in range(i + 1, len(body)):
                if body[i].position == body[j].position:
                    return True
        return False

    def update(self):
        global GAME_ON
        self.snake.update_position()
        self.snake.update_direction()
        if self.check_snake_collision():
            GAME_ON = False
        if self.snake.head.position == self.apple.position:
            self.score += 1
            self.snake.grow()
            self.spawn_apple()

    def set_board(self):
        self.score = 0
        self.snake = Snake(self.width // 2 - 1, self.height // 2 - 1)
        self.apple = Apple(Position(self.width // 2 - 1, self.height // 2 - 3))

    def spawn_apple(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        self.apple.move(Position(x, y))

    def get_screen_size(self) -> (int, int):
        return self.width * self.cell_width, self.height * self.cell_width

    def turn(self, direction: Direction):
        snake_dir = self.snake.head.direction
        if snake_dir != direction and snake_dir.value + direction.value != Position(0, 0):
            board.snake.change_direction(direction)

    def draw_score(self):
        font = pg.font.SysFont('Comic Sans MS', 100)
        text_surface = font.render(f'Score: {self.score}', True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))

    def draw(self):
        screen.fill(self.background_color)
        self.apple.draw()
        self.snake.draw()
        self.draw_score()


def draw_game_over():
    text_surface = FONT.render('Game Over', True, (0, 0, 0))
    screen.blit(text_surface, (board.get_screen_size()[0] / 3, board.get_screen_size()[1] / 3))


with open("palette.txt") as f:
    PALETTE = list(map(lambda x: x.rstrip('\n'), f.readlines()))

pg.font.init()
FONT = pg.font.SysFont('Comic Sans MS', 200)

WIDTH = 50
HEIGHT = 30
CELL_WIDTH = 50
board = Board(CELL_WIDTH, WIDTH, HEIGHT, pg.Color('#9CC75D'))
pg.init()
clock = pg.time.Clock()

screen = pg.display.set_mode(board.get_screen_size())
key_to_direction = {
    pg.K_LEFT: Direction.L,
    pg.K_RIGHT: Direction.R,
    pg.K_UP: Direction.U,
    pg.K_DOWN: Direction.D
}

GAME_ON = True
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYUP:
            if event.key == pg.K_r:
                board.set_board()
                GAME_ON = True
            if new_direction := key_to_direction.get(event.key):
                board.turn(new_direction)
    if GAME_ON:
        board.update()
        board.draw()
    else:
        draw_game_over()
    pg.display.flip()
    clock.tick(20)