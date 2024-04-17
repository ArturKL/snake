from __future__ import annotations
from typing import Tuple

import pygame as pg
import random
from enum import Enum
import sys


class Position:
    """
        Represents a position in 2D space.
    """
    
    x: int
    y: int

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Position) -> Position:
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, other: int) -> Position:
        return Position(self.x * other, self.y * other)

    def __str__(self) -> str:
        return f'<x: {self.x} y: {self.y}>'

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y


class Direction(Enum):
    """
        An enum representing different directions in 2D space.
    """
    N = Position(0, 0)
    U = Position(0, -1)
    D = Position(0, 1)
    L = Position(-1, 0)
    R = Position(1, 0)


class Segment:
    """
    Represents a segment of the Snake.
    """

    color: pg.Color
    position: Position
    direction: Direction
    is_head: bool

    def __init__(self, color: pg.Color, position: Position, direction: Direction, head: bool = False):
        self.color = color
        self.position = position
        self.direction = direction
        self.is_head = head

    def set_direction(self, direction: Direction):
        """
        Set the direction of the segment.
        """
        self.direction = direction

    def draw(self):
        """
        Draw the segment on the screen.
        """
        pg.draw.rect(screen, pg.Color('white'),
                     pg.Rect(self.position.x * CELL_WIDTH + 1,
                             self.position.y * CELL_WIDTH + 1,
                             CELL_WIDTH - 2,
                             CELL_WIDTH - 2))

class Snake:
    """
    Represents a Snake in the game.
    """

    head: Segment
    body: list[Segment]

    @staticmethod
    def rand_color() -> pg.Color:
        """
        Returns a random color from the palette.
        """
        color: str = random.choice(PALETTE)
        return pg.Color(color)

    def __init__(self, x: int, y: int):
        """
        Initialize a Snake with a given head position.
        """
        self.head = Segment(self.rand_color(), Position(x, y), Direction.N, True)
        self.body = list()

    def grow(self):
        """
        Grow the Snake by adding a new segment at the end.
        """
        last_segment: Segment = self.body[-1] if self.body else self.head
        direction: Direction = last_segment.direction
        position: Position = last_segment.position - direction.value
        new_segment: Segment = Segment(self.rand_color(), position, direction)
        self.body.append(new_segment)

    def update_direction(self):
        """
        Update the direction of each segment based on the previous segment's direction.
        """
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].direction = self.body[i - 1].direction
        if self.body:
            self.body[0].direction = self.head.direction

    def update_position(self):
        """
        Update the position of each segment based on its direction.
        """
        self.head.position += self.head.direction.value
        for seg in self.body:
            seg.position += seg.direction.value

    def change_direction(self, direction: Direction):
        """
        Change the direction of the Snake's head.
        """
        self.head.direction = direction

    def draw(self):
        """
        Draw all the segments of the Snake on the screen.
        """
        self.head.draw()
        for segment in self.body:
            segment.draw()


class Apple:
    """
    Represents an Apple in the game.
    """
    position: Position

    def __init__(self, position: Position):
        self.position = position

    def move(self, new_position: Position):
        """
        Move the Apple to a new position.
        """
        self.position = new_position

    def draw(self):
        """
        Draw the Apple on the screen.
        """
        # Draw a red rectangular shape representing the Apple
        pg.draw.rect(screen, pg.Color('red'),
                    pg.Rect(self.position.x * CELL_WIDTH,  # x-coordinate of the top-left corner
                            self.position.y * CELL_WIDTH,  # y-coordinate of the top-left corner
                            CELL_WIDTH,                    # width of the rectangular shape
                            CELL_WIDTH))                   # height of the rectangular shape


class Board:
    """
    Represents the game board.
    """
    height: int
    width: int
    cell_width: int
    background_color: pg.Color
    score: int
    apple: Apple
    snake: Snake

    def __init__(self, cell_width: int, width: int, height: int, background_color: pg.Color):
        self.height = height
        self.width = width
        self.cell_width = cell_width
        self.background_color = background_color
        self.set_board()

    def check_snake_collision(self) -> bool:
        """
        Check if the snake has collided with the wall or its own body.
        """
        head_pos: Position = self.snake.head.position
        if head_pos.x < 0 or head_pos.y < 0 or head_pos.x >= self.width or head_pos.y >= self.height:
            return True
        body: list[Segment] = self.snake.body
        for i in range(len(body)):
            if body[i].position == head_pos:
                return True
            for j in range(i + 1, len(body)):
                if body[i].position == body[j].position:
                    return True
        return False

    def update(self):
        """
        Update the game board by updating the snake and checking for collisions.
        """
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
        """
        Set up the initial state of the game board.
        """
        self.score = 0
        self.snake = Snake(self.width // 2 - 1, self.height // 2 - 1)
        self.apple = Apple(Position(self.width // 2 - 1, self.height // 2 - 3))

    def spawn_apple(self):
        """
        Spawn a new apple at a random position on the board.
        """
        x: int = random.randint(1, self.width - 2)
        y: int = random.randint(1, self.height - 2)
        self.apple.move(Position(x, y))

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the size of the screen.
        """
        return self.width * self.cell_width, self.height * self.cell_width

    def turn(self, direction: Direction):
        """
        Change the direction of the snake.
        """
        snake_dir: Direction = self.snake.head.direction
        if snake_dir != direction and snake_dir.value + direction.value != Position(0, 0):
            board.snake.change_direction(direction)

    def draw_score(self):
        """
        Draw the current score on the screen.
        """
        font: pg.font.Font = pg.font.SysFont('Comic Sans MS', 25)
        text_surface = font.render(f'Score: {self.score}', True, FONT_COLOR)
        screen.blit(text_surface, (10, 10))

    def draw(self):
        """
        Draw the game board on the screen.
        """
        screen.fill(self.background_color)
        self.apple.draw()
        self.snake.draw()
        self.draw_score()


def draw_game_over():
    """
    Draw the "Game Over" text on the screen.
    """
    # Render the text surface and blit it to the screen
    text_surface: pg.Surface = FONT.render('Game Over', True, FONT_COLOR)
    screen.blit(text_surface, (board.get_screen_size()[0] / 3, board.get_screen_size()[1] / 3))


def get_cell_pos(row: int, col: int) -> Tuple[int, int]:
    """
    Return the coordinates of a cell in the game board.
    """
    return row * CELL_WIDTH, col * CELL_WIDTH


# Load the color palette from a text file
with open("palette.txt") as f:
    PALETTE: list[str] = list(map(lambda x: x.rstrip('\n'), f.readlines()))

# Initialize the Pygame font module and set up the font and color for rendering text
pg.font.init()
FONT: pg.font.Font = pg.font.SysFont('Comic Sans MS', 50)
FONT_COLOR: pg.Color = pg.Color('white')

# Set up the game board
WIDTH: int = 25  # Number of columns
HEIGHT: int = 15  # Number of rows
CELL_WIDTH: int = 30
board: Board = Board(CELL_WIDTH, WIDTH, HEIGHT, pg.Color('black'))

# Initialize Pygame and set up the display
pg.init()
clock: pg.time.Clock = pg.time.Clock()
screen: pg.Surface = pg.display.set_mode(board.get_screen_size())  # Set up the display window

# Set up the keyboard event handlers
key_to_direction = {
    pg.K_LEFT: Direction.L,
    pg.K_RIGHT: Direction.R,
    pg.K_UP: Direction.U,
    pg.K_DOWN: Direction.D
}

GAME_ON = True  # Flag to track the game status

# Main game loop
while True:
    # Handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                board.set_board()  # Reset the game board
                GAME_ON = True
            if new_direction := key_to_direction.get(event.key):
                board.turn(new_direction)
            break

    if GAME_ON:
        board.update()  # Update the snake and check for collisions
        board.draw()
    else:
        draw_game_over()

    # Update the display
    pg.display.flip()
    clock.tick(20)
