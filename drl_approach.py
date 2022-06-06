import copy
import time
from math import exp


import ax as ax
import numpy as np

import matplotlib.pyplot as plt
from keras.distribute.multi_worker_testing_utils import lock
from matplotlib.ticker import MultipleLocator

import Environment1
# import Environment4
import Environment5
import Environment3
import Environment0
# import Environment2_
import Environment2
import Node
import Server

import Agent
import torchNN_Agent

np.set_printoptions(threshold=np.inf)

server = Server.Server()
nodes = []
master_agents = []
worker_agents = []

a = []
for i in range(9):
    a.append([])

for i in range(Environment2.N):
    nodes.append(Node.Node())
    # print("master init", i)
    master_agents.append(torchNN_Agent.MasterAgent())
    for w in range(torchNN_Agent.worker_num):
        worker_agents.append(torchNN_Agent.WorkerAgent())


# m_addresses_a = ['models/case3_model/model_1_a', 'models/case3_model/model_2_a', 'models/case3_model/model_3_a', 'models/case3_model/model_4_a', 'models/case3_model/model_5_a', 'models/case3_model/model_6_a', 'models/case3_model/model_7_a', 'models/case3_model/model_8_a', 'models/case3_model/model_9_a', 'models/case3_model/model_10_a', 'models/case3_model/model_11_a', 'models/case3_model/model_12_a', 'models/case3_model/model_13_a', 'models/case3_model/model_14_a', 'models/case3_model/model_15_a', 'models/case3_model/model_16_a', 'models/case3_model/model_17_a', 'models/case3_model/model_18_a', 'models/case3_model/model_19_a', 'models/case3_model/model_20_a', 'models/case3_model/model_21_a', 'models/case3_model/model_22_a', 'models/case3_model/model_23_a', 'models/case3_model/model_24_a', 'models/case3_model/model_25_a']
# m_addresses_c = ['models/case3_model/model_1_c', 'models/case3_model/model_2_c', 'models/case3_model/model_3_c', 'models/case3_model/model_4_c', 'models/case3_model/model_5_c', 'models/case3_model/model_6_c', 'models/case3_model/model_7_c', 'models/case3_model/model_8_c', 'models/case3_model/model_9_c', 'models/case3_model/model_10_c', 'models/case3_model/model_11_c', 'models/case3_model/model_12_c', 'models/case3_model/model_13_c', 'models/case3_model/model_14_c', 'models/case3_model/model_15_c', 'models/case3_model/model_16_c', 'models/case3_model/model_17_c', 'models/case3_model/model_18_c', 'models/case3_model/model_19_c', 'models/case3_model/model_20_c', 'models/case3_model/model_21_c', 'models/case3_model/model_22_c', 'models/case3_model/model_23_c', 'models/case3_model/model_24_c', 'models/case3_model/model_25_c']
#
# w_addresses_a = ['models/case3_model/model_1_1_a', 'models/case3_model/model_1_2_a', 'models/case3_model/model_1_3_a', 'models/case3_model/model_1_4_a', 'models/case3_model/model_1_5_a', 'models/case3_model/model_2_1_a', 'models/case3_model/model_2_2_a', 'models/case3_model/model_2_3_a', 'models/case3_model/model_2_4_a', 'models/case3_model/model_2_5_a', 'models/case3_model/model_3_1_a', 'models/case3_model/model_3_2_a', 'models/case3_model/model_3_3_a', 'models/case3_model/model_3_4_a', 'models/case3_model/model_3_5_a', 'models/case3_model/model_4_1_a', 'models/case3_model/model_4_2_a', 'models/case3_model/model_4_3_a', 'models/case3_model/model_4_4_a', 'models/case3_model/model_4_5_a', 'models/case3_model/model_5_1_a', 'models/case3_model/model_5_2_a', 'models/case3_model/model_5_3_a', 'models/case3_model/model_5_4_a', 'models/case3_model/model_5_5_a', 'models/case3_model/model_6_1_a', 'models/case3_model/model_6_2_a', 'models/case3_model/model_6_3_a', 'models/case3_model/model_6_4_a', 'models/case3_model/model_6_5_a', 'models/case3_model/model_7_1_a', 'models/case3_model/model_7_2_a', 'models/case3_model/model_7_3_a', 'models/case3_model/model_7_4_a', 'models/case3_model/model_7_5_a', 'models/case3_model/model_8_1_a', 'models/case3_model/model_8_2_a', 'models/case3_model/model_8_3_a', 'models/case3_model/model_8_4_a', 'models/case3_model/model_8_5_a', 'models/case3_model/model_9_1_a', 'models/case3_model/model_9_2_a', 'models/case3_model/model_9_3_a', 'models/case3_model/model_9_4_a', 'models/case3_model/model_9_5_a', 'models/case3_model/model_10_1_a', 'models/case3_model/model_10_2_a', 'models/case3_model/model_10_3_a', 'models/case3_model/model_10_4_a', 'models/case3_model/model_10_5_a', 'models/case3_model/model_11_1_a', 'models/case3_model/model_11_2_a', 'models/case3_model/model_11_3_a', 'models/case3_model/model_11_4_a', 'models/case3_model/model_11_5_a', 'models/case3_model/model_12_1_a', 'models/case3_model/model_12_2_a', 'models/case3_model/model_12_3_a', 'models/case3_model/model_12_4_a', 'models/case3_model/model_12_5_a', 'models/case3_model/model_13_1_a', 'models/case3_model/model_13_2_a', 'models/case3_model/model_13_3_a', 'models/case3_model/model_13_4_a', 'models/case3_model/model_13_5_a', 'models/case3_model/model_14_1_a', 'models/case3_model/model_14_2_a', 'models/case3_model/model_14_3_a', 'models/case3_model/model_14_4_a', 'models/case3_model/model_14_5_a', 'models/case3_model/model_15_1_a', 'models/case3_model/model_15_2_a', 'models/case3_model/model_15_3_a', 'models/case3_model/model_15_4_a', 'models/case3_model/model_15_5_a', 'models/case3_model/model_16_1_a', 'models/case3_model/model_16_2_a', 'models/case3_model/model_16_3_a', 'models/case3_model/model_16_4_a', 'models/case3_model/model_16_5_a', 'models/case3_model/model_17_1_a', 'models/case3_model/model_17_2_a', 'models/case3_model/model_17_3_a', 'models/case3_model/model_17_4_a', 'models/case3_model/model_17_5_a', 'models/case3_model/model_18_1_a', 'models/case3_model/model_18_2_a', 'models/case3_model/model_18_3_a', 'models/case3_model/model_18_4_a', 'models/case3_model/model_18_5_a', 'models/case3_model/model_19_1_a', 'models/case3_model/model_19_2_a', 'models/case3_model/model_19_3_a', 'models/case3_model/model_19_4_a', 'models/case3_model/model_19_5_a', 'models/case3_model/model_20_1_a', 'models/case3_model/model_20_2_a', 'models/case3_model/model_20_3_a', 'models/case3_model/model_20_4_a', 'models/case3_model/model_20_5_a', 'models/case3_model/model_21_1_a', 'models/case3_model/model_21_2_a', 'models/case3_model/model_21_3_a', 'models/case3_model/model_21_4_a', 'models/case3_model/model_21_5_a', 'models/case3_model/model_22_1_a', 'models/case3_model/model_22_2_a', 'models/case3_model/model_22_3_a', 'models/case3_model/model_22_4_a', 'models/case3_model/model_22_5_a', 'models/case3_model/model_23_1_a', 'models/case3_model/model_23_2_a', 'models/case3_model/model_23_3_a', 'models/case3_model/model_23_4_a', 'models/case3_model/model_23_5_a', 'models/case3_model/model_24_1_a', 'models/case3_model/model_24_2_a', 'models/case3_model/model_24_3_a', 'models/case3_model/model_24_4_a', 'models/case3_model/model_24_5_a', 'models/case3_model/model_25_1_a', 'models/case3_model/model_25_2_a', 'models/case3_model/model_25_3_a', 'models/case3_model/model_25_4_a', 'models/case3_model/model_25_5_a']
# w_addresses_c = ['models/case3_model/model_1_1_c', 'models/case3_model/model_1_2_c', 'models/case3_model/model_1_3_c', 'models/case3_model/model_1_4_c', 'models/case3_model/model_1_5_c', 'models/case3_model/model_2_1_c', 'models/case3_model/model_2_2_c', 'models/case3_model/model_2_3_c', 'models/case3_model/model_2_4_c', 'models/case3_model/model_2_5_c', 'models/case3_model/model_3_1_c', 'models/case3_model/model_3_2_c', 'models/case3_model/model_3_3_c', 'models/case3_model/model_3_4_c', 'models/case3_model/model_3_5_c', 'models/case3_model/model_4_1_c', 'models/case3_model/model_4_2_c', 'models/case3_model/model_4_3_c', 'models/case3_model/model_4_4_c', 'models/case3_model/model_4_5_c', 'models/case3_model/model_5_1_c', 'models/case3_model/model_5_2_c', 'models/case3_model/model_5_3_c', 'models/case3_model/model_5_4_c', 'models/case3_model/model_5_5_c', 'models/case3_model/model_6_1_c', 'models/case3_model/model_6_2_c', 'models/case3_model/model_6_3_c', 'models/case3_model/model_6_4_c', 'models/case3_model/model_6_5_c', 'models/case3_model/model_7_1_c', 'models/case3_model/model_7_2_c', 'models/case3_model/model_7_3_c', 'models/case3_model/model_7_4_c', 'models/case3_model/model_7_5_c', 'models/case3_model/model_8_1_c', 'models/case3_model/model_8_2_c', 'models/case3_model/model_8_3_c', 'models/case3_model/model_8_4_c', 'models/case3_model/model_8_5_c', 'models/case3_model/model_9_1_c', 'models/case3_model/model_9_2_c', 'models/case3_model/model_9_3_c', 'models/case3_model/model_9_4_c', 'models/case3_model/model_9_5_c', 'models/case3_model/model_10_1_c', 'models/case3_model/model_10_2_c', 'models/case3_model/model_10_3_c', 'models/case3_model/model_10_4_c', 'models/case3_model/model_10_5_c', 'models/case3_model/model_11_1_c', 'models/case3_model/model_11_2_c', 'models/case3_model/model_11_3_c', 'models/case3_model/model_11_4_c', 'models/case3_model/model_11_5_c', 'models/case3_model/model_12_1_c', 'models/case3_model/model_12_2_c', 'models/case3_model/model_12_3_c', 'models/case3_model/model_12_4_c', 'models/case3_model/model_12_5_c', 'models/case3_model/model_13_1_c', 'models/case3_model/model_13_2_c', 'models/case3_model/model_13_3_c', 'models/case3_model/model_13_4_c', 'models/case3_model/model_13_5_c', 'models/case3_model/model_14_1_c', 'models/case3_model/model_14_2_c', 'models/case3_model/model_14_3_c', 'models/case3_model/model_14_4_c', 'models/case3_model/model_14_5_c', 'models/case3_model/model_15_1_c', 'models/case3_model/model_15_2_c', 'models/case3_model/model_15_3_c', 'models/case3_model/model_15_4_c', 'models/case3_model/model_15_5_c', 'models/case3_model/model_16_1_c', 'models/case3_model/model_16_2_c', 'models/case3_model/model_16_3_c', 'models/case3_model/model_16_4_c', 'models/case3_model/model_16_5_c', 'models/case3_model/model_17_1_c', 'models/case3_model/model_17_2_c', 'models/case3_model/model_17_3_c', 'models/case3_model/model_17_4_c', 'models/case3_model/model_17_5_c', 'models/case3_model/model_18_1_c', 'models/case3_model/model_18_2_c', 'models/case3_model/model_18_3_c', 'models/case3_model/model_18_4_c', 'models/case3_model/model_18_5_c', 'models/case3_model/model_19_1_c', 'models/case3_model/model_19_2_c', 'models/case3_model/model_19_3_c', 'models/case3_model/model_19_4_c', 'models/case3_model/model_19_5_c', 'models/case3_model/model_20_1_c', 'models/case3_model/model_20_2_c', 'models/case3_model/model_20_3_c', 'models/case3_model/model_20_4_c', 'models/case3_model/model_20_5_c', 'models/case3_model/model_21_1_c', 'models/case3_model/model_21_2_c', 'models/case3_model/model_21_3_c', 'models/case3_model/model_21_4_c', 'models/case3_model/model_21_5_c', 'models/case3_model/model_22_1_c', 'models/case3_model/model_22_2_c', 'models/case3_model/model_22_3_c', 'models/case3_model/model_22_4_c', 'models/case3_model/model_22_5_c', 'models/case3_model/model_23_1_c', 'models/case3_model/model_23_2_c', 'models/case3_model/model_23_3_c', 'models/case3_model/model_23_4_c', 'models/case3_model/model_23_5_c', 'models/case3_model/model_24_1_c', 'models/case3_model/model_24_2_c', 'models/case3_model/model_24_3_c', 'models/case3_model/model_24_4_c', 'models/case3_model/model_24_5_c', 'models/case3_model/model_25_1_c', 'models/case3_model/model_25_2_c', 'models/case3_model/model_25_3_c', 'models/case3_model/model_25_4_c', 'models/case3_model/model_25_5_c']



m_addresses_a = ['models/model_1_a', 'models/model_2_a', 'models/model_3_a', 'models/model_4_a']
m_addresses_c = ['models/model_1_c', 'models/model_2_c', 'models/model_3_c', 'models/model_4_c']
w_addresses_a = ['models/model_1_1_a', 'models/model_1_2_a', 'models/model_1_3_a', 'models/model_1_4_a', 'models/model_1_5_a',
               'models/model_2_1_a', 'models/model_2_2_a', 'models/model_2_3_a', 'models/model_2_4_a', 'models/model_2_5_a',
               'models/model_3_1_a', 'models/model_3_2_a', 'models/model_3_3_a', 'models/model_3_4_a', 'models/model_3_5_a',
               'models/model_4_1_a', 'models/model_4_2_a', 'models/model_4_3_a', 'models/model_4_4_a', 'models/model_4_5_a']
w_addresses_c = ['models/model_1_1_c', 'models/model_1_2_c', 'models/model_1_3_c', 'models/model_1_4_c', 'models/model_1_5_c',
               'models/model_2_1_c', 'models/model_2_2_c', 'models/model_2_3_c', 'models/model_2_4_c', 'models/model_2_5_c',
               'models/model_3_1_c', 'models/model_3_2_c', 'models/model_3_3_c', 'models/model_3_4_c', 'models/model_3_5_c',
               'models/model_4_1_c', 'models/model_4_2_c', 'models/model_4_3_c', 'models/model_4_4_c', 'models/model_4_5_c']

for i in range(len(master_agents)):
    master_agents[i].actor_address = m_addresses_a[i]
    master_agents[i].critic_address = m_addresses_c[i]
    master_agents[i].save_model()
for i in range(len(worker_agents)):
    worker_agents[i].actor_address = w_addresses_a[i]
    worker_agents[i].critic_address = w_addresses_c[i]
    worker_agents[i].save_model()

for _ in range(len(master_agents)):
    for n in range(_ * torchNN_Agent.worker_num, _ * torchNN_Agent.worker_num + 5):
        worker_agents[n].update_nn(master_agents[_])


def drl_process(lr):
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    decision_flag = []
    for _ in range(Environment2.N):
        decision_flag.append(0)

    satisfied = 0
    # target_request: int
    # target_node: int

    for t in range(Environment2.T):
        # if t % 10000 == 0:
        #     print("time", t)
        come = []
        come_delay = []
        for _ in range(Environment2.R):
            if Environment2.arr[_] == t:
                come.append(req[_])
                come_delay.append(Environment2.d[_])

        for _ in range(Environment2.N):
            decision_flag[_] = 0

        # collect from nodes
        server.clear_finish_delay()
        for _ in range(Environment2.N):
            server.collect(nodes[_].send(), nodes[_].send_delay())
        finished = server.send_finish_delay()
        # print("finished:", finished)
        for _ in range(len(finished)):
            if t + 1 <= finished[_]:
                satisfied += 1
                # print("satisfied:", finished[_], _)

        # receive new coming requests
        server.receive(come, come_delay)

        # print("task", server.task)

        # distribution
        while server.task:
            target_request = server.send()
            # print("target", target_request)
            target_request_delay = server.send_delay()
            target_node = target_request[0][0]
            nodes[target_node - 1].receive(target_request, target_request_delay)

        # print("after distribution:")
        # for n in range(Environment2.N):
        #     print(nodes[n].queue, nodes[n].processing)

        # drl
        for _ in range(Environment2.N):
            if nodes[_].processing == -1 and nodes[_].queue:
                decision_flag[_] = 1
                master_agents[_].recognize(nodes[_], t)
                master_agents[_].generate()
                for _n in range(_ * torchNN_Agent.worker_num, _ * torchNN_Agent.worker_num + 5):
                    worker_agents[_n].update_nn(master_agents[_])
                    worker_agents[_n].receive(master_agents[_], t)
                    worker_agents[_n].generate()
                    worker_agents[_n].decide()
                    worker_agents[_n].update_virtual_node(nodes[_])
                    worker_agents[_n].virtual_process()
                    worker_agents[_n].recognize(t)
                    worker_agents[_n].get_exp(t)
                    master_agents[_].receive_exp(worker_agents[_n])

                master_agents[_].to_np()
                master_agents[_].update(lr)
                master_agents[_].to_list()
                master_agents[_].clear_exp()

                nodes[_].set_processing(master_agents[_].decide())

        # print("before transition")
        # for n in range(Environment2.N):
        #     print(nodes[n].queue, nodes[n].processing)

        for _ in range(Environment2.N):
            # print("queue", nodes[_].queue)
            # print("decide", nodes[_].processing)
            nodes[_].transition()
            if decision_flag[_] == 1:
                master_agents[_].acc_reward += nodes[_].count_reward(t + 1)

    return satisfied


acc_rewards = [[], [], [], [], []]
ratio = []
start = time.time()
lr = 0.02
for j in range(100):
    print('episode', j)
    proc = drl_process(lr)
    print("total:", server.total)
    print("satisfied:", proc)
    ratio.append(proc / server.total)
    server.clear()
    for i in range(len(nodes)):
        nodes[i].clear()
    for i in range(len(master_agents)):
        print('acc_rewards', master_agents[i].acc_reward)
        acc_rewards[i].append(master_agents[i].acc_reward)
        # for parameters in master_agents[i].ActorNetwork.parameters():
        #     print('master agent', i, parameters)
        master_agents[i].acc_reward = 0
    lr *= 0.95
end = time.time()
period = end - start
print("time:", period)
print('acc', acc_rewards)
print('ratio', ratio)
