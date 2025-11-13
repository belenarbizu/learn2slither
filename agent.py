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
        pass


    def train_step(self, state, action, reward, next_state, done):
        pass
