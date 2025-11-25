import random
import pygame
from zmq import Enum

REWARDS = {"GREEN": 20,
          "RED": -10,
          "DEATH": -40,
          "EMPTY": -0.1}

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
        self.direction = random.choice(list(Direction))
        self.head = (random.randint(0, (self.w // self.block_size - 1)) * self.block_size, random.randint(0, (self.h // self.block_size - 1)) * self.block_size)
        # Initialize the snake body with the head position and 2 more values
        self.snake = [self.head, (self.head[0] - self.block_size, self.head[1]), (self.head[0] - (2 * self.block_size), self.head[1])]
        self.score = 0
        self.green_apples = []
        self.red_apple = None
        self.place_food()
        self.update()


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
            reward = REWARDS["RED"]
            self.red_apple = None
            if len(self.snake) > 1:
                self.snake.pop()
            if len(self.snake) > 1:
                self.snake.pop()
            self.place_food()
        else:
            self.snake.pop()  # remove tail (the last element of the list)

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
        while self.red_apple is None:
            x = random.randint(0, (self.w // self.block_size - 1)) * self.block_size
            y = random.randint(0, (self.h // self.block_size - 1)) * self.block_size
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

    def get_state(self):
        """
        Estado mejorado: peligro relativo + comida relativa
        11 features en total
        """
        head = self.head
        
        # Calcular puntos en direcciones relativas (recto, derecha, izquierda)
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        
        # Direcciones relativas a donde mira la serpiente
        dir_straight = clock_wise[idx]
        dir_right = clock_wise[(idx + 1) % 4]
        dir_left = clock_wise[(idx - 1) % 4]
        
        # Puntos a verificar
        point_straight = self._get_point_in_direction(head, dir_straight)
        point_right = self._get_point_in_direction(head, dir_right)
        point_left = self._get_point_in_direction(head, dir_left)
        
        # PELIGRO en direcciones relativas (3 features)
        danger_straight = self.is_collision(point_straight)
        danger_right = self.is_collision(point_right)
        danger_left = self.is_collision(point_left)
        
        # COMIDA VERDE: dirección relativa (4 features)
        green_left, green_right, green_up, green_down = self._get_food_direction(
            self.green_apples
        )
        
        # COMIDA ROJA: dirección relativa (4 features)
        red_left, red_right, red_up, red_down = self._get_food_direction(
            [self.red_apple] if self.red_apple else []
        )
        
        state = [
            # Peligro relativo (3)
            danger_straight,
            danger_right,
            danger_left,
            
            # Dirección de comida verde (4)
            green_left,
            green_right,
            green_up,
            green_down,
            
            # Dirección de comida roja (4)
            red_left,
            red_right,
            red_up,
            red_down,
        ]
        
        return [int(x) for x in state]
    
    def _get_point_in_direction(self, point, direction):
        """Obtiene el punto en una dirección específica"""
        x, y = point
        if direction == Direction.UP:
            y -= self.block_size
        elif direction == Direction.DOWN:
            y += self.block_size
        elif direction == Direction.LEFT:
            x -= self.block_size
        elif direction == Direction.RIGHT:
            x += self.block_size
        return (x, y)
    
    def _get_food_direction(self, food_list):
        """
        Retorna dirección de la comida más cercana
        Returns: [izquierda, derecha, arriba, abajo]
        """
        if not food_list:
            return [0, 0, 0, 0]
        
        # Encontrar comida más cercana (distancia Manhattan)
        closest = min(food_list, 
                     key=lambda f: abs(f[0] - self.head[0]) + abs(f[1] - self.head[1]))
        
        food_left = int(closest[0] < self.head[0])
        food_right = int(closest[0] > self.head[0])
        food_up = int(closest[1] < self.head[1])
        food_down = int(closest[1] > self.head[1])
        
        return [food_left, food_right, food_up, food_down]