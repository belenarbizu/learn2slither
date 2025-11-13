import random
import pygame
from zmq import Enum

REWARDS = {"GREEN": 10,
          "RED": -10,
          "DEATH": -20,
          "EMPTY": -0.5}

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Game:
    def __init__(self, w=760, h=520, block_size=40):
        self.w = w
        self.h = h
        self.block_size = block_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()
        self.reset()

    
    def reset(self):
        self.direction = random.choice(list(Direction))
        self.head = (random.randint(0, (self.w // self.block_size - 1) * self.block_size), random.randint(0, (self.h // self.block_size - 1) * self.block_size))
        # Initialize the snake body with the head position and 2 more values
        self.snake = [self.head, (self.head[0] - self.block_size, self.head[1]), (self.head[0] - 2 * self.block_size, self.head[1])]
        self.score = 0
        self.green_apples = []
        self.red_apple = None
        self.place_food()


    def update(self):
        self.screen.fill("grey")

        for body in self.snake:
            pygame.draw.rect(self.screen, "blue", pygame.Rect(body[0], body[1], self.block_size, self.block_size))
        
        for apple in self.green_apples:
            pygame.draw.circle(self.screen, "green", (apple[0] + self.block_size // 2, apple[1] + self.block_size // 2), self.block_size // 2)
        
        if self.red_apple:
            pygame.draw.circle(self.screen, "red", (self.red_apple[0] + self.block_size // 2, self.red_apple[1] + self.block_size // 2), self.block_size // 2)

        pygame.display.flip()


    def play_step(self, action):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self.move(action)  # update the head
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision(self.head) or len(self.snake) <= 0:
            game_over = True
            reward = REWARDS["DEATH"]
            return reward, game_over, self.score

        if self.head in self.green_apples:
            self.score += 1
            reward = REWARDS["GREEN"]
            self.green_apples.remove(self.head)
            self.place_food()
        elif self.head == self.red_apple:
            game_over = True
            reward = REWARDS["RED"]
            return reward, game_over, self.score
        else:
            self.snake.pop()

        self.update()
        self.clock.tick(60)  # limits FPS to 60

        return reward, game_over, self.score


    def place_food(self):
        # Place food at a random location not occupied by the snake
        while len(self.green_apples) < 2:
            x = random.randint(0, (self.w // self.block_size - 1) * self.block_size)
            y = random.randint(0, (self.h // self.block_size - 1) * self.block_size)
            if (x, y) not in self.snake and (x, y) != self.red_apple:
                self.green_apples.append((x, y))
        while self.red_apple is None:
            x = random.randint(0, (self.w // self.block_size - 1) * self.block_size)
            y = random.randint(0, (self.h // self.block_size - 1) * self.block_size)
            if (x, y) not in self.snake and (x, y) not in self.green_apples:
                self.red_apple = (x, y)


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
    

    def get_state(self):
        head = self.head
        left = (head[0] - self.block_size, head[1])
        right = (head[0] + self.block_size, head[1])
        up = (head[0], head[1] - self.block_size)
        down = (head[0], head[1] + self.block_size)