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
    def __init__(self, block_size=40):
        self.w = BOARD_SIZE * block_size
        self.h = BOARD_SIZE * block_size
        self.block_size = block_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()
        self.reset()

    
    def reset(self):
        self.move_history = []
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

        self.move_history.append({"head": self.head, "move": self.direction})

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
    

    # def get_state(self):
    #     left = (self.head[0] - self.block_size, self.head[1])
    #     right = (self.head[0] + self.block_size, self.head[1])
    #     up = (self.head[0], self.head[1] - self.block_size)
    #     down = (self.head[0], self.head[1] + self.block_size)

    #     dir_left = 1 if self.direction == Direction.LEFT else 0
    #     dir_right = 1 if self.direction == Direction.RIGHT else 0
    #     dir_up = 1 if self.direction == Direction.UP else 0
    #     dir_down = 1 if self.direction == Direction.DOWN else 0

    #     # clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    #     # idx = clock_wise.index(self.direction)
    #     # next_dir = clock_wise[(idx + 1) % 4]
    #     # prev_dir = clock_wise[(idx - 1) % 4]

    #     danger_left = dir_left and self.is_collision(left)
    #     danger_right = dir_right and self.is_collision(right)
    #     danger_up = dir_up and self.is_collision(up)
    #     danger_down = dir_down and self.is_collision(down)

    #     red_apple_left = 1 if (self.red_apple[0] < self.head[0] and self.red_apple[1] == self.head[1]) else 0
    #     red_apple_right = 1 if (self.red_apple[0] > self.head[0] and self.red_apple[1] == self.head[1]) else 0
    #     red_apple_up = 1 if (self.red_apple[1] < self.head[1] and self.red_apple[0] == self.head[0]) else 0

    #     green_apple_left = 1 if any(apple[0] < self.head[0] and apple[1] == self.head[1] for apple in self.green_apples) else 0
    #     green_apple_right = 1 if any(apple[0] > self.head[0] and apple[1] == self.head[1] for apple in self.green_apples) else 0
    #     green_apple_up = 1 if any(apple[1] < self.head[1] and apple[0] == self.head[0] for apple in self.green_apples) else 0

    #     state = [
    #         dir_left,
    #         dir_right,
    #         dir_up,
    #         dir_down,
    #         danger_left,
    #         danger_right,
    #         danger_up,
    #         danger_down,
    #         red_apple_left,
    #         red_apple_right,
    #         red_apple_up,
    #         green_apple_left,
    #         green_apple_right,
    #         green_apple_up
    #     ]

    #     return state


    def _is_there_point(self, from_point, to_points, direction):
        """ Given a starting point, a list of points and a direction,
            return True if there is a point directly in the given direction
            from the starting point
        """
        if direction == Direction.RIGHT:
            return any([from_point[0] < to_point[0]
                        and from_point[1] == to_point[1]
                        for to_point in to_points])
        elif direction == Direction.LEFT:
            return any([from_point[0] > to_point[0]
                        and from_point[1] == to_point[1]
                        for to_point in to_points])
        elif direction == Direction.UP:
            return any([from_point[1] > to_point[1]
                        and from_point[0] == to_point[0]
                        for to_point in to_points])
        elif direction == Direction.DOWN:
            return any([from_point[1] < to_point[1]
                        and from_point[0] == to_point[0]
                        for to_point in to_points])

        return False

    def _move_index(self):
        """ Return how much the snake is currently moving
        """
        if len(self.move_history) < 2:
            return 1

        coordinates = [move['head'] for move in self.move_history[-10:]]
        x = np.array([point[0] for point in coordinates])
        y = np.array([point[1] for point in coordinates])
        std_dev = np.mean([
            np.std(x),
            np.std(y)
        ]) / self.block_size

        return std_dev


    def get_state(self):
        """ Return the current state of the game
        """
        head = self.snake[0] if len(self.snake) > 0 else self.head
        direct_left = (head[0] - self.block_size, head[1])
        direct_right = (head[0] + self.block_size, head[1])
        direct_up = (head[0], head[1] - self.block_size)
        direct_down = (head[0], head[1] + self.block_size)

        dir_l = self.direction == Direction.LEFT
        dir_r = self.direction == Direction.RIGHT
        dir_u = self.direction == Direction.UP
        dir_d = self.direction == Direction.DOWN

        clock = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]

        current = clock.index(self.direction)
        straight = clock[current]
        left = clock[(current - 1) % 4]
        right = clock[(current + 1) % 4]

        previous = self.move_history[-2]['move'] if len(
            self.move_history) > 1 else self.direction
        previous = clock.index(previous)
        last_move_straight = previous == current
        last_move_left = previous == (current - 1) % 4
        last_move_right = previous == (current + 1) % 4

        danger_straight = (dir_r and self.is_collision(direct_right)) or (dir_l and self.is_collision(direct_left)) or (dir_u and self.is_collision(direct_up)) or (dir_d and self.is_collision(direct_down))
        danger_left = (dir_d and self.is_collision(direct_right)) or (dir_u and self.is_collision(direct_left)) or (dir_r and self.is_collision(direct_up)) or (dir_l and self.is_collision(direct_down))
        danger_right = (dir_u and self.is_collision(direct_right)) or (dir_d and self.is_collision(direct_left)) or (dir_l and self.is_collision(direct_up)) or (dir_r and self.is_collision(direct_down))

        green_apple_straight = self._is_there_point(head, self.green_apples, straight)
        green_apple_left = self._is_there_point(head, self.green_apples, left)
        green_apple_right = self._is_there_point(head, self.green_apples, right)
        red_apple_straight = self._is_there_point(head, self.red_apple, straight)
        red_apple_left = self._is_there_point(head, self.red_apple, left)
        red_apple_right = self._is_there_point(head, self.red_apple, right)


        state = [
            self._move_index(),
            last_move_straight,
            last_move_left,
            last_move_right,
            danger_straight,
            danger_left,
            danger_right,
            green_apple_straight,
            green_apple_left,
            green_apple_right,
            red_apple_straight,
            red_apple_left,
            red_apple_right
        ]

        return state