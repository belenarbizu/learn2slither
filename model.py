import torch
import torch.nn as nn
import torch.nn.functional as F # includes activation functions like ReLU

class Model(nn.Module):

    def __init__(self, n_observations, n_actions):
        super().__init__()
        self.layer1 = nn.Linear(n_observations, 42, dtype=torch.float32)
        self.layer2 = nn.Linear(42, 42, dtype=torch.float32)
        self.layer3 = nn.Linear(42, n_actions, dtype=torch.float32)


    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = self.layer3(x)
        return x


    def save(self, filename):
        torch.save(self.state_dict(), filename)