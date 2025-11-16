import torch
import random
import numpy as np
from collections import deque #for memory
from model import Model
import torch.optim as optim
import torch.nn as nn

class Agent:
    def __init__(self, batch_size, lr):
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=100_000)
        self.batch_size = batch_size
        self.model = Model(13, 3)  # neural network model
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
    

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
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        state = torch.unsqueeze(state, 0)
        next_state = torch.unsqueeze(next_state, 0)
        action = torch.unsqueeze(action, 0)
        reward = torch.unsqueeze(reward, 0)
        done = (done, )

        # use the model to predict the Q values for the current state
        pred = self.model(state)

        # clone the prediction to create the target tensor
        target = pred.clone()
        
