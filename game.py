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


    def _normalize_distance(self, distance):
        return 1.0 / distance


    def _scan_direction(self, head, dx, dy):
        """
        Mira desde la cabeza en línea recta y devuelve:
        [snake_body, green_apple, red_apple, wall, normalized_distance]
        """

        x, y = head
        distance = 1
        object_found = None   # "snake", "green", "red", "wall"

        # avanzar una casilla en la dirección dada
        x += dx
        y += dy

        while True:
            # 1. Si salimos del tablero → pared
            if x < 0 or x >= self.w or y < 0 or y >= self.h:
                object_found = "wall"
                break

            pos = (x, y)

            # 2. ¿Es cuerpo del snake?
            if pos in self.snake[1:]:  # cuerpo, excluye la cabeza
                object_found = "snake"
                break

            # 3. ¿Es manzana verde?
            if pos in self.green_apples:
                object_found = "green"
                break

            # 4. ¿Es manzana roja?
            if pos in self.red_apple:
                object_found = "red"
                break

            # avanzar otra casilla
            x += dx
            y += dy
            distance += 1

        # codificamos el resultado como vector de 5 posiciones:
        # [snake_body, green, red, wall, distance_norm]
        result = [0, 0, 0, 0, 0]

        if object_found == "snake":
            result[0] = 1
        elif object_found == "green":
            result[1] = 1
        elif object_found == "red":
            result[2] = 1
        elif object_found == "wall":
            result[3] = 1

        # normalizamos la distancia → más cerca = mayor valor
        result[4] = self._normalize_distance(distance)

        return result


    def get_state(self):
        """
        Devuelve un vector de 24 valores:
        4 = dirección actual one-hot
        4×5 = visión left/right/up/down
        """

        head = self.head

        # --- 1. Dirección actual ---
        dir_left  = 1 if self.direction == Direction.LEFT  else 0
        dir_right = 1 if self.direction == Direction.RIGHT else 0
        dir_up    = 1 if self.direction == Direction.UP    else 0
        dir_down  = 1 if self.direction == Direction.DOWN  else 0

        direction_state = [dir_left, dir_right, dir_up, dir_down]

        # --- 2. Visión en 4 direcciones ---
        # OJO: tu juego usa bloques con tamaño block_size
        # pero para visión NO queremos saltar bloques,
        # queremos mover en píxeles usando block_size.

        bs = self.block_size

        look_left  = self._scan_direction(head, -bs, 0)
        look_right = self._scan_direction(head,  bs, 0)
        look_up    = self._scan_direction(head, 0, -bs)
        look_down  = self._scan_direction(head, 0,  bs)

        # Concatenar todo en un mismo vector
        state = (
            direction_state +
            look_left +
            look_right +
            look_up +
            look_down
        )

        return state
