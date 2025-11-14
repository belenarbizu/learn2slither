import torch
import random
import numpy as np
from collections import deque #for memory

class Agent:
    def __init__(self, batch_size):
        self.epsilon = 0  # randomness
        self.gamma = 0  # discount rate
        self.memory = deque(maxlen=100_000)
        self.batch_size = batch_size
        self.model = None  # neural network model
    

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def train_long_memory(self):
        if len(self.memory) > self.batch_size:
            mini_sample = random.sample(self.memory, self.batch_size)
        else:
            mini_sample = self.memory
        
        for state, action, reward, next_state, done in mini_sample:
            self.train_step(state, action, reward, next_state, done)
    

    def train_short_memory(self, state, action, reward, next_state, done):
        self.train_step(state, action, reward, next_state, done)

    
    def get_action(self, state):
        action = [0, 0, 0] #no down

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            action[move] = 1
        else:
            # convert state list to state tensor so PyTorch model can process it
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_tensor)
            move = torch.argmax(prediction).item()
            action[move] = 1

        return action


    def train_step(self, state, action, reward, next_state, done):
        pass
