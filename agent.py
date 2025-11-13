import torch
import random
import numpy as np
from collections import deque #for memory

class Agent:
    def __init__(self):
        self.epsilon = 0  # randomness
        self.gamma = 0  # discount rate
        self.memory = deque(maxlen=100_000)
    

    def remember(self, state, action, reward, next_state, done):
        pass


    def train_long_memory(self):
        pass
    

    def train_short_memory(self):
        pass

    
    def get_action(self, state):
        pass
