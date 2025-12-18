import random
import pygame
from zmq import Enum
import numpy as np

REWARDS = {"GREEN": 25,
          "RED": -25,
          "DEATH": -100,
          "EMPTY": -0.01}

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

BOARD_SIZE = 10

class Game:
    def __init__(self, block_size=80):
        self.w = BOARD_SIZE * block_size
        self.h = BOARD_SIZE * block_size
        self.block_size = block_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()
        self.reset()

    
    def reset(self):
        self.direction = random.choice(list(Direction))
        self.head = (random.randint(0, (self.w // self.block_size - 1)) * self.block_size, random.randint(0, (self.h // self.block_size - 1)) * self.block_size)
        
        # Initialize the snake body with the head position and 2 more values
        if self.direction == Direction.UP:
            self.snake = [self.head, (self.head[0], self.head[1] - self.block_size), (self.head[0], self.head[1] - (2 * self.block_size))]
        elif self.direction == Direction.DOWN:
            self.snake = [self.head, (self.head[0], self.head[1] + self.block_size), (self.head[0], self.head[1] + (2 * self.block_size))]
        elif self.direction == Direction.LEFT:
            self.snake = [self.head, (self.head[0] - self.block_size, self.head[1]), (self.head[0] - (2 * self.block_size), self.head[1])]
        elif self.direction == Direction.RIGHT:
            self.snake = [self.head, (self.head[0] + self.block_size, self.head[1]), (self.head[0] + (2 * self.block_size), self.head[1])]

        self.score = 0
        self.green_apples = []
        self.red_apple = []
        self.place_food()
        self.update()


    def update(self):
        self.screen.fill("grey")

        for body in self.snake:
            pygame.draw.rect(self.screen, "blue", pygame.Rect(body[0], body[1], self.block_size, self.block_size))
        
        for apple in self.green_apples:
            pygame.draw.circle(self.screen, "green", (apple[0] + self.block_size // 2, apple[1] + self.block_size // 2), self.block_size // 2)
        
        for apple in self.red_apple:
            pygame.draw.circle(self.screen, "red", (apple[0] + self.block_size // 2, apple[1] + self.block_size // 2), self.block_size // 2)

        pygame.display.flip()


    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        # action = [straight, right, left]
        if action[0] == 1:  # no change
            new_dir = clock_wise[idx]
        elif action[1] == 1:  # right turn r -> d -> l -> u
            new_dir = clock_wise[(idx + 1) % 4]
        else:  # left turn r -> u -> l -> d
            new_dir = clock_wise[(idx - 1) % 4]
        self.direction = new_dir

        self.move(self.direction)  # update the head
        self.snake.insert(0, self.head) # add new head to the snake body in position 0

        reward = REWARDS["EMPTY"]
        game_over = False
        
        if self.head in self.green_apples:
            self.score += 1
            reward = REWARDS["GREEN"]
            self.green_apples.remove(self.head)
            self.place_food()
        elif self.head in self.red_apple:
            reward = REWARDS["RED"]
            self.red_apple.remove(self.head)
            if len(self.snake) > 1:
                self.snake.pop()
            if len(self.snake) > 1:
                self.snake.pop()
            self.place_food()
        else:
            self.snake.pop()  # remove tail (the last element of the list)

        if self.is_collision(self.head) or len(self.snake) <= 0:
            game_over = True
            reward = REWARDS["DEATH"]
            return reward, game_over, self.score

        self.update()
        self.clock.tick(60)  # limits FPS to 60

        return reward, game_over, self.score


    def place_food(self):
        # Place food at a random location not occupied by the snake
        while len(self.green_apples) < 2:
            x = random.randint(0, (self.w // self.block_size - 1)) * self.block_size
            y = random.randint(0, (self.h // self.block_size - 1)) * self.block_size
            if (x, y) not in self.snake and (x, y) != self.red_apple:
                self.green_apples.append((x, y))
        while len(self.red_apple) < 1:
            x = random.randint(0, (self.w // self.block_size - 1)) * self.block_size
            y = random.randint(0, (self.h // self.block_size - 1)) * self.block_size
            if (x, y) not in self.snake and (x, y) not in self.green_apples:
                self.red_apple.append((x, y))


    def is_collision(self, position):
        x, y = position
        # Check for collision with walls
        if x < 0 or x > self.w - self.block_size or y < 0 or y > self.h - self.block_size:
            return True
        # Check for collision with the snake's body
        if position in self.snake[1:]:
            return True
        return False


    def move(self, direction):
        x = self.head[0]
        y = self.head[1]
        if direction == Direction.UP:
            y -= self.block_size
        elif direction == Direction.DOWN:
            y += self.block_size
        elif direction == Direction.LEFT:
            x -= self.block_size
        elif direction == Direction.RIGHT:
            x += self.block_size
        self.head = (x, y)
    

    def get_position_in_direction(self, direction):
        x = self.head[0]
        y = self.head[1]
        if direction == Direction.UP:
            y -= self.block_size
        elif direction == Direction.DOWN:
            y += self.block_size
        elif direction == Direction.LEFT:
            x -= self.block_size
        elif direction == Direction.RIGHT:
            x += self.block_size
        return (x, y)


    def get_state(self):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        straight = clock_wise[idx]
        right = clock_wise[(idx + 1) % 4]
        left = clock_wise[(idx - 1) % 4]

        danger_left = 1 if self.is_collision(self.get_position_in_direction(left)) else 0
        danger_right = 1 if self.is_collision(self.get_position_in_direction(right)) else 0
        danger_up = 1 if self.is_collision(self.get_position_in_direction(straight)) else 0

        red_apple_left = 1 if self.get_position_in_direction(left) in self.red_apple else 0
        red_apple_right = 1 if self.get_position_in_direction(right) in self.red_apple else 0
        red_apple_up = 1 if self.get_position_in_direction(straight) in self.red_apple else 0

        green_apple_left = 1 if self.get_position_in_direction(left) in self.green_apples else 0
        green_apple_right = 1 if self.get_position_in_direction(right) in self.green_apples else 0
        green_apple_up = 1 if self.get_position_in_direction(straight) in self.green_apples else 0

        state = [
            danger_left,
            danger_right,
            danger_up,
            red_apple_left,
            red_apple_right,
            red_apple_up,
            green_apple_left,
            green_apple_right,
            green_apple_up
        ]

        return state
