import torch
import random
from collections import deque #for memory
from model import Model
import torch.optim as optim
import torch.nn as nn

class Agent:
    def __init__(self, batch_size, lr):
        self.epsilon = 1.0  # randomness
        self.gamma = 0.95  # discount rate
        self.memory = deque(maxlen=100_000)
        self.batch_size = batch_size
        self.model = Model(9, 3)  # neural network model
        self.target = Model(9, 3)
        self.target.load_state_dict(self.model.state_dict())
        self.target.eval()

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.update_count = 0
        self.target_update = 100
    

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def train_long_memory(self):
        if len(self.memory) > self.batch_size:
            mini_sample = random.sample(self.memory, self.batch_size)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.train_step(states, actions, rewards, next_states, dones)
    

    def train_short_memory(self, state, action, reward, next_state, done):
        self.train_step(state, action, reward, next_state, done)

    
    def get_action(self, state):
        action = [0, 0, 0] #no down

        if random.uniform(0, 1) < self.epsilon:
            move = random.randint(0, 2)
            action[move] = 1
        else:
            # convert state list to state tensor so PyTorch model can process it
            with torch.no_grad():
                state_tensor = torch.tensor(state, dtype=torch.float32)
                prediction = self.model(state_tensor)
                move = prediction.argmax().item()
                action[move] = 1

        return action


    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)


        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # use the model to predict the Q values for the current state
        pred = self.model(state)

        # clone the prediction to create the target tensor
        target = pred.clone()

        for i in range(len(done)):
          with torch.no_grad():
            Q_new = reward[i]
            if not done[i]:
                Q_new = reward[i] + (self.gamma * torch.max(self.target(next_state[i])))
            target[i][torch.argmax(action[i]).item()] = Q_new
        
        self.optimizer.zero_grad()
        # compute the loss between the target and predicted Q values
        loss = self.criterion(target, pred)
        # backpropagate the loss and update the model parameters
        loss.backward()
        self.optimizer.step()

        self.update_count += 1
        if self.update_count % self.target_update == 0:
            self.target.load_state_dict(self.model.state_dict())

        
