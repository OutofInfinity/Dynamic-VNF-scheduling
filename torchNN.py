import torch
import torch.nn.functional as F
from torch import nn
import Environment2
import Environment2_

buff_size = Environment2.rSize
state_size = buff_size * 5
gamma = 0.5


class ActorNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5*buff_size, 30)
        self.fc2 = nn.Linear(30, 20)
        self.fc3 = nn.Linear(20, 20)
        self.fc4 = nn.Linear(20, buff_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = torch.clamp(F.softmax(self.fc4(x), dim=-1), min=1e-4, max=1-1e-4)
        return x


class CriticNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5*buff_size, 30)
        self.fc2 = nn.Linear(30, 20)
        self.fc3 = nn.Linear(20, 20)
        self.fc4 = nn.Linear(20, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x


def actor_loss(prob, act, adv):
    ans = 0
    for i in range(len(act)):
        ans += -torch.log(prob[act[i]]) * adv[i]
    ans /= len(act)
    return ans


def critic_loss(rewards, n_states, current_state):
    ans = 0
    for i in range(len(rewards)):
        temp = rewards[i] + gamma * n_states[i] - current_state
        ans += torch.pow(temp, 2)
    ans /= len(rewards)
    return ans
