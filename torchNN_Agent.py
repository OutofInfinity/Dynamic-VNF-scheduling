import copy
import random

import torch
import numpy as np

import torchNN
import Node

worker_num = 5
PHI1 = 0.4
PHI2 = 0.2
PHI3 = 0.4
gamma = 0.5



class WorkerAgent:
    def __init__(self):
        self.ActorNetwork = torchNN.ActorNetwork()
        self.CriticNetwork = torchNN.CriticNetwork()
        self.actor_address = ''
        self.critic_address = ''

        self.state = []
        self.n_state = []
        self.req_num = 0

        self.act_prob = []

        self.vt = 0
        self.n_vt = 0
        self.r = 0
        self.adv = 0

        self.act_num = -1

        self.virtual_node = Node.Node()
        self.t = 0

    def save_model(self):
        torch.save(self.ActorNetwork, self.actor_address)
        torch.save(self.CriticNetwork, self.critic_address)

    def receive(self, master, t):
        self.state = copy.deepcopy(master.state)
        self.req_num = master.req_num
        self.t = t

    def generate(self):
        actor = torch.load(self.actor_address)
        critic = torch.load(self.critic_address)
        self.act_prob = actor(self.state)
        self.vt = critic(self.state)

    def decide(self):
        p_sum = 0
        for i in range(self.req_num):
            p_sum += self.act_prob[i]
        x = random.uniform(0, p_sum)
        # print("x", x)
        # print("act", self.act_prob)
        # print("req_num", self.req_num)
        # print("p_sum", p_sum)
        cumulative_probability = 0
        for i in range(self.req_num):
            cumulative_probability += self.act_prob[i]
            if x <= cumulative_probability:
                self.act_num = i
                break
        # print("act_num", self.act_num)

    def update_virtual_node(self, node):
        self.virtual_node.processing = node.processing
        self.virtual_node.queue = copy.deepcopy(node.queue)
        self.virtual_node.finish = copy.deepcopy(node.finish)
        self.virtual_node.finish_delay = node.finish_delay
        self.virtual_node.delay = copy.deepcopy(node.delay)
        self.virtual_node.wait = copy.deepcopy(node.wait)
        self.virtual_node.m_delay = copy.deepcopy(node.m_delay)

    def virtual_process(self):
        self.virtual_node.set_processing(self.act_num)
        # print("v queue", self.virtual_node.queue)
        # print("v pro", self.virtual_node.processing)
        self.virtual_node.transition()

    def recognize(self, t):
        self.n_state = []

        for i in range(len(self.virtual_node.queue)):
            if self.virtual_node.processing == i:
                self.n_state.append(1)
            else:
                self.n_state.append(2)

            self.n_state.append(self.virtual_node.queue[i][0][1])
            self.n_state.append(len(self.virtual_node.queue[i]))
            self.n_state.append(self.virtual_node.delay[i] - t - 1)
            self.n_state.append(self.virtual_node.wait[i])
        while len(self.n_state) < torchNN.state_size:
            self.n_state.append(0)

        self.n_state = np.array(self.n_state, dtype=np.float32)
        self.n_state = torch.from_numpy(self.n_state)

    def get_exp(self, t):
        critic = torch.load(self.critic_address)

        first = 0
        if self.virtual_node.finish == [-1, -1]:
            if self.t + 1 <= self.virtual_node.finish_delay:
                first = 1
        d_sum = 0
        ddl_sum = 0
        over = 0
        for i in range(len(self.virtual_node.delay)):
            d_sum += self.virtual_node.delay[i] - t - 1
            ddl_sum += self.virtual_node.delay[i]
            if t + 1 - self.virtual_node.delay[i] < 0:
                over += 1
        if ddl_sum == 0:
            second = 1
        else:
            second = d_sum / ddl_sum
        if len(self.virtual_node.delay) == 0:
            third = 0
        else:
            third = over / len(self.virtual_node.delay)
            # print("agent third", third)

        self.r = PHI1 * first + PHI2 * second - PHI3 * third
        # print("agent r", first, second, third)
        # print("n_state", self.n_state)
        self.n_vt = critic(self.n_state)
        # print("n_state_v", self.ACNetwork.state_v)

        # print("vt", self.vt)
        # print("n_vt", self.n_vt)
        self.adv = self.r + torchNN.gamma * self.n_vt - self.vt
        # print("adv", adv)

    def update_nn(self, master):
        actor = torch.load(master.actor_address)
        critic = torch.load(master.critic_address)
        torch.save(actor, self.actor_address)
        torch.save(critic, self.critic_address)


class MasterAgent:
    def __init__(self):
        self.ActorNetwork = torchNN.ActorNetwork()
        self.CriticNetwork = torchNN.CriticNetwork()
        self.actor_address = ''
        self.critic_address = ''

        self.state = []

        self.act_prob = []
        self.act_nums = []
        self.ads = []

        self.rewards = []
        self.n_vts = []
        self.vt = 0

        self.req_num = 0

        self.acc_reward = 0
        self.episode_flag = 0

        self.act_decision = 0

    def save_model(self):
        torch.save(self.ActorNetwork, self.actor_address)
        torch.save(self.CriticNetwork, self.critic_address)

    def recognize(self, node, t):
        self.req_num = len(node.queue)
        self.state = []
        for i in range(len(node.queue)):
            if node.processing == i:
                self.state.append(1)
            else:
                self.state.append(2)

            self.state.append(node.queue[i][0][1])
            self.state.append(len(node.queue[i]))
            self.state.append(node.delay[i] - t)
            self.state.append(node.wait[i])

        while len(self.state) < torchNN.state_size:
            self.state.append(0)

        self.state = np.array(self.state, dtype=np.float32)
        self.state = torch.from_numpy(self.state)

    def generate(self):
        actor = torch.load(self.actor_address)
        critic = torch.load(self.critic_address)
        self.vt = critic(self.state)
        self.act_prob = actor(self.state)

    def receive_exp(self, worker):
        self.act_nums.append(worker.act_num)
        self.ads.append(worker.adv)

        self.rewards.append(worker.r)
        self.n_vts.append(worker.n_vt)

    def clear_exp(self):
        self.act_nums.clear()
        self.ads.clear()

        self.rewards.clear()
        self.n_vts.clear()

    def to_np(self):
        self.act_nums = np.array(self.act_nums, dtype=np.float32)
        self.ads = np.array(self.ads, dtype=np.float32)

        self.rewards = np.array(self.rewards, dtype=np.float32)
        self.n_vts = np.array(self.n_vts, dtype=np.float32)

    def to_list(self):
        self.act_nums = list(self.act_nums)
        self.ads = list(self.ads)

        self.rewards = list(self.rewards)
        self.n_vts = list(self.n_vts)

    def update(self, learning_rate):
        actor = torch.load(self.actor_address)
        critic = torch.load(self.critic_address)

        act = torch.from_numpy(self.act_nums).long()
        adv = torch.from_numpy(self.ads)

        rwd = torch.from_numpy(self.rewards)
        n_vt = torch.from_numpy(self.n_vts)

        # print('before')
        # for parameters in actor.parameters():
        #     print(parameters[0])
        # print('probs', self.act_prob, act, adv)

        # state_tensor = torch.from_numpy(self.state)
        act_p = actor(self.state)
        # print('state', self.state)
        # print('act', act_p)
        a_loss = actor_loss(act_p, act, adv)
        # print('aloss', a_loss)
        optimizer_a = torch.optim.SGD(actor.parameters(), lr=learning_rate)
        optimizer_a.zero_grad()
        a_loss.backward()
        optimizer_a.step()
        # print('after')
        # for parameters in actor.parameters():
        #     print(parameters[0])
        # print('grad')
        # for x in optimizer_a.param_groups[0]['params']:
        #     print(x.grad)
        state_v = critic(self.state)
        v_loss = critic_loss(rwd, n_vt, state_v)
        optimizer_v = torch.optim.SGD(critic.parameters(), lr=learning_rate)
        optimizer_v.zero_grad()
        v_loss.backward()
        optimizer_v.step()

        torch.save(actor, self.actor_address)
        torch.save(critic, self.critic_address)

    def decide(self):
        actor = torch.load(self.actor_address)
        act_prob = actor(self.state)
        decision = 0
        max_prob = act_prob[0]
        for i in range(self.req_num):
            if act_prob[i] > max_prob:
                decision = i
                max_prob = act_prob[i]
        return decision


def critic_loss(rewards, n_states, current_state):
    ans = 0
    for i in range(len(rewards)):
        temp = rewards[i] + gamma * n_states[i] - current_state
        ans += torch.pow(temp, 2)
    ans /= len(rewards)
    return ans


def actor_loss(prob, act, adv):
    ans = 0
    for i in range(len(act)):
        ans += -torch.log(prob[act[i]]) * adv[i]
    ans /= len(act)
    return ans
