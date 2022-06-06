import copy
import random
import threading
import time
from asyncio import locks
from math import exp

import _thread

import ax as ax
import numpy
import numpy as np

import matplotlib.pyplot as plt
from keras.distribute.multi_worker_testing_utils import lock
from matplotlib.ticker import MultipleLocator

import Environment1
# import Environment4
import Environment5
import Environment3
import Environment0
import Environment2_
import Environment2
import Node
import Server
import Solver
import Agent

# import Env

# for i in range(Environment.R):
#     print("request", i + 1, Environment.r[i])
#
# print("arrival time:", Environment.arr)
# print("total processing time:", Environment.process_t)
# print("delay constraints:", Environment.d)

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
    master_agents.append(Agent.MasterAgent())
    for w in range(Agent.W):
        worker_agents.append(Agent.WorkerAgent())


def process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)
    print("req:", req)

    satisfied = 0
    # target_request: int
    # target_node: int
    for t in range(Environment2.T):
        come = []
        come_delay = []
        # flag = 0
        # for _t in Environment2.arr:
        #     if _t == t:
        #         flag = 1
        # for _n in nodes:
        #     if _n.queue:
        #         flag = 1
        # if flag == 1:
        for j in range(Environment2.R):
            if Environment2.arr[j] == t:
                come.append(req[j])
                come_delay.append(Environment2.d[j])

        # collect from nodes
        server.clear_finish_delay()
        for j in range(Environment2.N):
            server.collect(nodes[j].send(), nodes[j].send_delay())
        finished = server.send_finish_delay()
        # print("finished:", finished)
        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1

        # receive new coming requests
        print("coming requests", come)
        server.receive(come, come_delay)

        # distribution
        while server.task:
            target_request = server.send()
            target_request_delay = server.send_delay()
            target_node = target_request[0][0]
            nodes[target_node - 1].receive(target_request, target_request_delay)

        # processing
        print("after distribution")
        for n in range(Environment2.N):
            if nodes[n].queue:
                print("node", n + 1, nodes[n].queue, "working", nodes[n].processing)

        for j in range(Environment2.N):
            nodes[j].transition()

        print("after transition")
        for n in range(Environment2.N):
            if nodes[n].queue:
                print("node", n + 1, nodes[n].queue, "working", nodes[n].processing)

    return satisfied


def quick_process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    server.__init__()
    for n in range(Environment2.N):
        nodes[n].__init__()

    satisfied = 0
    event = []
    t = 0

    while t < Environment2.T:
        for at in Environment2.arr:
            if at > t:
                event.append(at)
        for n in nodes:
            if n.queue:
                event.append(t + n.queue[n.processing][0][1])

        t = min(event)
        # print("t", t)
        come = []
        come_delay = []

        for j in range(Environment2.R):
            if Environment2.arr[j] == t:
                come.append(req[j])
                come_delay.append(Environment2.d[j])

        # collect from nodes
        server.clear_finish_delay()
        for j in range(Environment2.N):
            server.collect(nodes[j].send(), nodes[j].send_delay())
        finished = server.send_finish_delay()

        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1

        # receive new coming requests
        server.receive(come, come_delay)

        # distribution
        while server.task:
            target_request = server.send()
            target_request_delay = server.send_delay()
            target_node = target_request[0][0]
            nodes[target_node - 1].receive(target_request, target_request_delay)

        # print("after distribution")
        # for n in range(Environment2.N):
        #     if nodes[n].queue:
        #         print("working", nodes[n].processing)

        for j in range(Environment2.N):
            nodes[j].quick_transition(t)

        # print("after transition")
        # for n in range(Environment2.N):
        #     if nodes[n].queue:
        #         print("node", n + 1, "len", len(nodes[n].queue), "working", nodes[n].processing)

        for j in range(Environment2.N):
            nodes[j].t = t

        event.clear()

    return satisfied


def simple_process(s_server, s_nodes, decision):
    satisfied = 0
    # target_request: int
    # target_node: int
    for t in range(Environment2.T):

        # collect from nodes
        s_server.clear_finish_delay()
        for j in range(Environment2.N):
            s_server.collect(s_nodes[j].send(), s_nodes[j].send_delay())
        finished = s_server.send_finish_delay()
        # print("finished:", finished)
        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1

        # distribution
        while s_server.task:
            target_request = s_server.send()
            target_request_delay = s_server.send_delay()
            target_node = target_request[0][0]
            s_nodes[target_node - 1].receive(target_request, target_request_delay)

        # processing
        for j in range(Environment2.N):
            s_nodes[j].transition()

        for n in range(Environment2.N):
            decision.append(s_nodes[n].processing)

    return satisfied


def quick_simple_process(s_server, s_nodes, decision):
    satisfied = 0
    event1 = []
    t = 0

    while t < Environment2.T:
        for n in s_nodes:
            if n.queue:
                event1.append(t + n.queue[n.processing][0][1])

        if event1:
            t = min(event1)

            # collect from nodes
            s_server.clear_finish_delay()
            for j in range(Environment2.N):
                s_server.collect(s_nodes[j].send(), s_nodes[j].send_delay())
            finished = s_server.send_finish_delay()

            for j in range(len(finished)):
                if t + 1 <= finished[j]:
                    satisfied += 1

            # distribution
            while s_server.task:
                target_request = s_server.send()
                target_request_delay = s_server.send_delay()
                target_node = target_request[0][0]
                s_nodes[target_node - 1].receive(target_request, target_request_delay)

            for j in range(Environment2.N):
                s_nodes[j].quick_transition(t)

            for n in range(Environment2.N):
                decision.append(s_nodes[n].processing)
        else:
            for n in range(Environment2.N):
                decision.append(s_nodes[n].processing)
            break

        for j in range(Environment2.N):
            s_nodes[j].t = t

        event1.clear()
    return satisfied

# E1: 13/117 E2: 34-50/352 E3: 14/30
def sa_process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    server.__init__()
    for n in range(Environment2.N):
        nodes[n].__init__()

    satisfied = 0
    # target_request: int
    # target_node: int
    for t in range(Environment2.T):
        if t % 10000 == 0:
            print('t', t)
        come = []
        come_delay = []
        for j in range(Environment2.R):
            if Environment2.arr[j] == t + 1:
                come.append(req[j])
                come_delay.append(Environment2.d[j])

        # collect from nodes
        server.clear_finish_delay()
        for j in range(Environment2.N):
            server.collect(nodes[j].send(), nodes[j].send_delay())
        finished = server.send_finish_delay()
        # print("finished:", finished)
        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1

        # receive new coming requests
        server.receive(come, come_delay)

        # distribution
        while server.task:
            target_request = server.send()
            target_request_delay = server.send_delay()
            target_node = target_request[0][0]
            nodes[target_node - 1].receive(target_request, target_request_delay)

        # sa
        temp = 10
        iteration = 100
        decay = 0.95
        s_server = copy.deepcopy(server)
        s_nodes = []
        for n in range(Environment2.N):
            s_node = copy.deepcopy(nodes[n])
            s_nodes.append(s_node)
        n_decision = []
        f = -simple_process(s_server, s_nodes, n_decision)
        decision = copy.deepcopy(n_decision)
        while temp > 0.05:
            n_decision = []
            f_new = -simple_process(s_server, s_nodes, n_decision)
            delta = f_new - f
            if delta < 0:
                f = f_new
                decision = copy.deepcopy(n_decision)
            else:
                prob = random.uniform(0, 1)
                if prob < exp(-delta / temp):
                    f = f_new
                    decision = copy.deepcopy(n_decision)
            temp = temp * decay
        for n in range(Environment2.N):
            nodes[n].set_processing(decision[n])

        # processing
        for j in range(Environment2.N):
            nodes[j].transition()

    return satisfied


def quick_sa_process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    server.__init__()
    for n in range(Environment2.N):
        nodes[n].__init__()

    satisfied = 0
    event = []
    t = 0

    while t < Environment2.T:
        for at in Environment2.arr:
            if at > t:
                event.append(at)
        for n in nodes:
            if n.queue:
                event.append(t + n.queue[n.processing][0][1])

        t = min(event)
        print("t", t)
        come = []
        come_delay = []

        for j in range(Environment2.R):
            if Environment2.arr[j] == t:
                come.append(req[j])
                come_delay.append(Environment2.d[j])

        # collect from nodes
        server.clear_finish_delay()
        for j in range(Environment2.N):
            server.collect(nodes[j].send(), nodes[j].send_delay())
        finished = server.send_finish_delay()

        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1

        # receive new coming requests
        server.receive(come, come_delay)

        # distribution
        while server.task:
            target_request = server.send()
            target_request_delay = server.send_delay()
            target_node = target_request[0][0]
            nodes[target_node - 1].receive(target_request, target_request_delay)

        # sa
        temp = 10
        decay = 0.95
        s_server = copy.deepcopy(server)
        s_nodes = []
        for n in range(Environment2.N):
            s_node = copy.deepcopy(nodes[n])
            s_nodes.append(s_node)
        n_decision = []
        f = -quick_simple_process(s_server, s_nodes, n_decision)
        decision = copy.deepcopy(n_decision)
        while temp > 0.05:
            n_decision = []
            f_new = -quick_simple_process(s_server, s_nodes, n_decision)

            delta = f_new - f
            if delta < 0:
                f = f_new
                decision = copy.deepcopy(n_decision)
            else:
                prob = random.uniform(0, 1)
                if prob < exp(-delta / temp):
                    f = f_new
                    decision = copy.deepcopy(n_decision)
            temp = temp * decay
        print("nodesl", len(nodes))
        print("decisionl", len(decision))
        for n in range(Environment2.N):
            nodes[n].set_processing(decision[n])

        for j in range(Environment2.N):
            nodes[j].quick_transition(t)

        print("after transition")
        for n in range(Environment2.N):
            if nodes[n].queue:
                print("node", n + 1,  "working", nodes[n].processing)

        for j in range(Environment2.N):
            nodes[j].t = t

        event.clear()

    return satisfied


# E1: 15/117 E2: 44/352 E3: 19/30
def ilp_process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    server.__init__()
    for n in range(Environment2.N):
        nodes[n].__init__()

    satisfied = 0
    # target_request: int
    # target_node: int
    for t in range(Environment2.T):
        print('time', t)
        come = []
        come_delay = []
        ilp_t = 0
        ilp_req = []
        ilp_d = []
        ilp_f = []
        ilp_rho = []
        ilp_vir = []
        offset = []
        for j in range(Environment2.R):
            if Environment2.arr[j] == t + 1:
                come.append(req[j])
                come_delay.append(Environment2.d[j])

        # collect from nodes
        server.clear_finish_delay()
        for j in range(Environment2.N):
            server.collect(nodes[j].send(), nodes[j].send_delay())
        finished = server.send_finish_delay()
        print("finished:", finished)
        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1
                print("satisfied:", finished[j], j)

        # receive new coming requests
        server.receive(come, come_delay)

        # distribution
        while server.task:
            target_request = server.send()
            target_request_delay = server.send_delay()
            target_node = target_request[0][0]
            nodes[target_node - 1].receive(target_request, target_request_delay)

        print("after distribution:")
        for n in range(Environment2.N):
            print(nodes[n].queue, nodes[n].processing)

        # ILP solve
        flag = 0
        for n in range(Environment2.N):
            if nodes[n].queue and nodes[n].processing == -1:
                flag = 1
                break
        if flag == 1:
            # ilp_req, ilp_d
            offset.append(0)
            rnum = 0
            for j in range(Environment2.N):
                for k in range(len(nodes[j].queue)):
                    ilp_req.append(copy.deepcopy(nodes[j].queue[k]))
                    d_remain = nodes[j].delay[k] - t
                    if d_remain >= 0:
                        ilp_d.append(nodes[j].delay[k] - t)
                    else:
                        ilp_d.append(0)
                    rnum += 1
                offset.append(rnum)
            offset.remove(offset[len(offset) - 1])
            # ilp_vir, ilp_t
            for j in range(len(ilp_req)):
                ilp_vir.append([])
                for k in range(len(ilp_req[j])):
                    ilp_vir[j].append(ilp_req[j][k][2])
                    ilp_t += ilp_req[j][k][1]
            # ilp_rho
            for n in range(Environment2.N):
                ilp_rho.append([])
                for r in range(len(ilp_req)):
                    ilp_rho[n].append([])
                    for v in range(Environment2.V):
                        ilp_rho[n][r].append(0)
            for r in range(len(ilp_req)):
                for j in range(len(ilp_req[r])):
                    ilp_rho[ilp_req[r][j][0] - 1][r][ilp_req[r][j][2]] = ilp_req[r][j][1]
            # ilp_f
            for n in range(Environment2.N):
                ilp_f.append([])
                for r in range(len(ilp_req)):
                    ilp_f[n].append([])
                    for v in range(Environment2.V):
                        if ilp_rho[n][r][v] > 0:
                            ilp_f[n][r].append(1)
                        else:
                            ilp_f[n][r].append(0)

            solver = Solver.Solver(Environment2.T * 2, Environment2.N, len(ilp_req), Environment2.V,
                                   ilp_d, ilp_f, ilp_rho, ilp_vir)
            arrange = solver.solve()
            if arrange:
                print("decided")
                for n in range(Environment2.N):
                    for r in range(len(ilp_req)):
                        for v in range(Environment2.V):
                            if arrange[n][r][v] == 1:
                                if nodes[n].processing == -1:
                                    print("r", r, "offset", offset[n])
                                    nodes[n].set_processing(r - offset[n])
                                    print(nodes[n].processing, n)
            else:
                print("no solution")

        # processing
        print("before transition")
        for n in range(Environment2.N):
            print(nodes[n].queue, nodes[n].processing)
        for j in range(Environment2.N):
            nodes[j].transition()

        print("after transition")
        for n in range(Environment2.N):
            print(nodes[n].queue, nodes[n].processing)

    return satisfied


def master_preprocess(master, node, t):
    master.clear_loss()
    master.recognize(node, t)
    master.generate()


def learn_process(master, worker, node, t):
    worker.receive(master.state, master.req_num, t)
    worker.generate()
    worker.decide()
    worker.create_virtual_node(node)
    worker.virtual_node.set_processing(worker.act_num)

    offset = 1
    while worker.virtual_node.queue:
        if worker.virtual_node.processing != -1:
            # processing
            # print("before transition")
            # for n in range(Environment2.N):
            worker.virtual_process()
            worker.recognize(t + offset)
            # worker.get_exp(t + offset)
            # worker.acc_r += worker.r
            # master.receive_exp(worker)
            # master.update()
            #
            # master.state = copy.deepcopy(master.n_state)
            worker.state = copy.deepcopy(worker.n_state)
            worker.req_num = len(worker.virtual_node.queue)
            offset += 1

        else:
            worker.generate()
            worker.decide()
            worker.virtual_node.set_processing(worker.act_num)

            worker.virtual_process()
            worker.recognize(t + offset)
            worker.get_exp(t + offset)
            worker.acc_r += worker.r
            master.receive_exp(worker)
            master.update()

            master.state = copy.deepcopy(master.n_state)
            worker.state = copy.deepcopy(worker.n_state)
            worker.req_num = len(worker.virtual_node.queue)
            offset += 1

    master.state = []
    master.recognize(node, t)
    master.generate()
    # print("a_loss", master.a_loss)
    # print("act_prob", master.ACNetwork.all_act_prob)
    master.init_loss()


def drl_process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    decision_flag = []
    for _ in range(Environment2.N):
        decision_flag.append(0)

    # server.__init__()
    # for n in range(Environment2.N):
    #     nodes[n].__init__()
    #     master_agents[n].__init__()
    # for n in range(len(worker_agents)):
    #     worker_agents[n].__init__()

    satisfied = 0
    # target_request: int
    # target_node: int

    for t in range(Environment2.T):
        print("time", t)
        come = []
        come_delay = []
        for _ in range(Environment2.R):
            if Environment2.arr[_] == t + 1:
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
        threads1 = []
        threads2 = []
        for _ in range(Environment2.N):
            if nodes[_].processing == -1 and nodes[_].queue:
                # print("master", _)
                decision_flag[_] = 1
                temp_thr = threading.Thread(target=master_preprocess, args=(master_agents[_], nodes[_], t))
                threads1.append(temp_thr)
                temp_thr.start()

                for k in range(_ * Agent.W, _ * Agent.W + Agent.W):
                    worker_agents[k].update_nn(master_agents[_])
                for k in range(_ * Agent.W, _ * Agent.W + Agent.W):
                    temp_thr2 = threading.Thread(target=learn_process,
                                                 args=(master_agents[_], worker_agents[k], nodes[_], t))
                    threads2.append(temp_thr2)
                    temp_thr2.start()
                for t_thr in threads2:
                    t_thr.join()
                nodes[_].set_processing(master_agents[_].decide())

        for t_thr in threads1:
            t_thr.join()

        # print("before transition")
        # for n in range(Environment2.N):
        #     print(nodes[n].queue, nodes[n].processing)

        for _ in range(Environment2.N):
            # print("queue", nodes[_].queue)
            # print("decide", nodes[_].processing)
            nodes[_].transition()
            if decision_flag[_] == 1:
                master_agents[_].acc_reward += nodes[_].count_reward(t + 1)

                # print("loss", master_agents[j].loss)
                # print("state", master_agents[j].state)

        # r_sum = 0
        # if (t + 1) % 45 == 0:
        #     print("episode", (t + 1) / 45)
        #     e = (t + 1) / 45
        #     for _ in range(len(master_agents)):
        #         avg_reward = master_agents[_].acc_reward / e
        #         r_sum += avg_reward
        #         print("master_acc", avg_reward)
        #         a[_].append(avg_reward)
        #
        #     r_sum /= Environment2.N
        #     print("avg", r_sum)
        #     a[8].append(r_sum)
        #     print("total:", server.total)
        #     print("satisfied:", satisfied)
        #     server.total = 0
        #     satisfied = 0

        # processing
        # print("before transition")
        # for n in range(Environment2.N):
        #     print(nodes[n].queue, nodes[n].processing)

        # for j in range(Environment2.N):
        #     nodes[j].transition()
        #
        # print("after transition")
        # for n in range(Environment2.N):
        #     print(nodes[n].queue, nodes[n].processing)

    return satisfied


def n_drl_process():
    req = []
    for p in range(Environment2.R):
        request = copy.deepcopy(Environment2.r[p])
        req.append(request)

    # server.__init__()
    # for n in range(Environment2.N):
    #     nodes[n].__init__()
    #     master_agents[n].__init__()
    # for n in range(len(worker_agents)):
    #     worker_agents[n].__init__()

    satisfied = 0
    # target_request: int
    # target_node: int

    for t in range(Environment2.T):
        print("time", t)
        come = []
        come_delay = []
        for j in range(Environment2.R):
            if Environment2.arr[j] == t + 1:
                come.append(req[j])
                come_delay.append(Environment2.d[j])

        # collect from nodes
        server.clear_finish_delay()
        for j in range(Environment2.N):
            server.collect(nodes[j].send(), nodes[j].send_delay())
        finished = server.send_finish_delay()
        # print("finished:", finished)
        for j in range(len(finished)):
            if t + 1 <= finished[j]:
                satisfied += 1

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
        for j in range(Environment2.N):
            if nodes[j].processing == -1 and nodes[j].queue:
                while master_agents[j].a_loss > 0.1:
                    print("master", j)
                    master_agents[j].clear_loss()
                    master_agents[j].recognize(nodes[j], t)
                    master_agents[j].generate()
                master_agents[j].init_loss()
                nodes[j].set_processing(master_agents[j].decide())

                # print("master", master_agents[j].ACNetwork.all_act_prob)
                # print("decide", nodes[j].processing)
        # processing
        print("before transition")
        for n in range(Environment2.N):
            print(nodes[n].queue, nodes[n].processing)

        for j in range(Environment2.N):
            nodes[j].transition()

        print("after transition")
        for n in range(Environment2.N):
            print(nodes[n].queue, nodes[n].processing)

    return satisfied


start = time.time()
max_ratio = 0
for j in range(1):
    proc = ilp_process()
    print("total:", server.total)
    print("satisfied:", proc)
    if proc / server.total > max_ratio:
        max_ratio = proc / server.total
    server.clear()
    for i in range(len(nodes)):
        nodes[i].clear()
end = time.time()
period = end - start
print("time:", period)
print('max', max_ratio)


# algorithms = ('DG', 'VNG', 'WG', 'SA', 'DRL')
# # # burst
# # # number = [0.07, 0.214, 0.19, 0.28, 0.439, 0.43]
# # # poisson
# # number = [0.02, 0.347, 0.04, 0.22, 0.67, 0.54]
# #
# number = [0.21, 0.21, 0.21, 0.22, 0.54]
# plt.xlabel("Approaches", fontsize=15)
# plt.ylabel("Ratio of delay satisfied reqs to all reqs", fontsize=15)
# y_major_locator = MultipleLocator(0.1)
# ax = plt.gca()
# ax.yaxis.set_major_locator(y_major_locator)
# plt.rcParams['savefig.dpi'] = 300  # 图片像素
# plt.rcParams['figure.dpi'] = 5000  # 分辨率
# plt.bar(algorithms, number, width=0.4, label='Ratio')
# for a, b in zip(algorithms, number):  # 柱子上的数字显示
#     plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=12)
# # for a, b in zip(index + width, num_list1):
# #     plt.text(a, b, '%.2f' % b, ha='center', va='bottom', fontsize=7)
# plt.ylim(0, 0.8)
# # plt.figure(dpi=300)
# plt.show()


# Poisson case
# x = [10, 11, 12, 13, 14, 15]
# dg = [0.02, 0.02, 0.02, 0.02, 0.0196, 0.0189]
# vng = [0.347, 0.34, 0.585, 0.396, 0.33, 0.327]
# wg = [0.04, 0.04, 0.04, 0.04, 0.04, 0.039]
# sa = [0.22, 0.128, 0.234, 0.15, 0.143, 0.106]
# ilp = [0.67, 0.48, 0.66, 0.55, 0.62, 0.59]
# drl = [0.53, 0.52, 0.42, 0.41, 0.41, 0.46]
# print(np.mean(drl))
# Burst case
# x = [10, 11, 12, 13, 14, 15]
# dg = [0.07, 0.023, 0.023, 0.023, 0.022, 0.022]
# vng = [0.214, 0.21, 0.2, 0.22, 0.196, 0.19]
# wg = [0.19, 0.14, 0.09, 0.068, 0.045, 0.04]
# sa = [0.28, 0.31, 0.256, 0.25, 0.24, 0.17]
# ilp = [0.439, 0.452, 0.465, 0.386, 0.4, 0.39] # '0.39'
# drl = [0.43, 0.4, 0.3, 0.31, 0.3, 0.24]
#
# real case
# x = [10, 11, 12, 13, 14, 15]
# dg = [0.21, 0.21, 0.21, 0.21, 0.21, 0.21]
# vng = [0.21, 0.21, 0.21, 0.21, 0.21, 0.21]
# wg = [0.21, 0.21, 0.21, 0.21, 0.21, 0.21]
# sa = [0.22, 0.21, 0.22, 0.21, 0.22, 0.21]
# drl = [0.54, 0.54, 0.54, 0.54, 0.54, 0.54]
#
# ln1, = plt.plot(x, dg, 'black', marker='.', linestyle=':', linewidth=1)
# ln2, = plt.plot(x, vng, "black", marker=',', linestyle='-', linewidth=1)
# ln3, = plt.plot(x, wg, "black", marker='o', linestyle='--', linewidth=1)
# ln4, = plt.plot(x, sa, "black", marker='s', linestyle='-.', linewidth=1)
# # ln5, = plt.plot(x, ilp, "black", marker='p', linestyle='-', linewidth=1)
# ln6, = plt.plot(x, drl, "black", marker='d', linestyle='--', linewidth=1)
#
# plt.legend(handles=[ln1, ln2, ln3, ln4, ln6], labels=['DG', 'VNG', 'WG', 'SA', 'DRL'], frameon=False, loc='best')
# plt.rcParams['savefig.dpi'] = 300 #图片像素
# plt.rcParams['figure.dpi'] = 5000 #分辨率
# plt.xlabel("Buffer size", fontsize=15)
# plt.ylabel("Ratio of delay satisfied reqs to all reqs", fontsize=15)
# plt.ylim(0, 1)
# plt.xlim(10, 15)
# plt.show()


# acc = [[-0.31189519020501966, -0.21654385076589222, -0.3225599482680961, -0.04613877202855732, -0.11777907413148728, -0.18537048810400802, -0.4280817585793547, -0.4145942705746304, -0.33609867921729075, -0.42812373981903357, -0.6450771563737433, -0.6305520579708582, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.6450771563737433, -0.9284104897070765, -0.9284104897070765, -0.9284104897070765, -1.066788868085455, -1.066788868085455, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192, -1.022052025980192], [7.755494351452547, 8.794925936576501, 9.803887261459128, 8.688524294762496, 8.688524294762496, 8.661497267735472, 8.661497267735472, 8.647909514232607, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.672813583146953, 8.704452942180117, 8.704452942180117, 8.704452942180117, 8.726208033765701, 8.660446532614817, 8.7898452440756, 8.716957592944544, 8.710668878823878, 8.679029519790713, 8.710668878823878, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713, 8.679029519790713], [-2.475949698220629, -5.2945008567406395, -6.469033222915704, -6.820061123456393, -3.0923349314196202, -2.121303616474274, -1.7189917525568372, -1.7276020841791073, -1.8846812643194664, -1.9179849887171294, -1.9080708720068575, -1.8908673780239411, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9080708720068575, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.887146939596742, -1.9134711668364186, -1.9134711668364186, -1.9134711668364186, -1.9341941975589283, -1.9106451203595112, -1.9317376617949678, -1.9110333627039864, -1.9428537619254491, -1.9165295346857725, -1.9428537619254491, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725, -1.9165295346857725], [0.5852515330456507, 0.5852515330456507, 0.5852515330456507, 0.5852515330456507, 0.5852515330456507, 0.6058397683397684, 0.6058397683397684, 0.6058397683397684, 0.6228383458646617, 0.6189976630766105, 0.6189976630766105, 0.6228383458646617, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105, 0.6189976630766105]]
# acc = [[-4.707460408021094, -4.707460408021094, -4.707460408021094, -4.870040263538289, -4.415591117118858, -4.415591117118858, -6.6422171151121745, -6.322386093874051, -6.272692381566336, -7.206347227471505, -6.691475519865648, -6.486792781486481, -7.247301078491274, -6.887125430567159, -8.664822001347188, -8.664822001347188, -8.311457755499923, -8.043896045349388, -8.04797064439265, -8.04797064439265, -8.284088987662114, -8.284088987662114, -7.847240379172457, -7.847240379172457, -5.0243285122633194, -5.0243285122633194, -5.003873966808774, -5.003873966808774, -4.97506474785871, -4.97506474785871, -9.054443570033078, -9.193274688167763, -9.310591255448033, -9.31443200265309, -9.31443200265309, -9.31443200265309, -7.706938771012753, -7.706938771012753, -7.706938771012753, -8.188733875286987, -8.158733875286988, -8.158733875286988, -8.158733875286988, -8.498330148578914, -8.23992471408267, -8.23992471408267, -8.718032758882444, -8.446747044596728, -8.37986734534861, -8.190393661138083, -7.996634262641844, -8.193889901739588, -8.313889901739586, -8.208889901739587, -7.071570483466232, -7.071570483466232, -7.043284769180518, -7.043284769180518, -6.823359957150442, -7.043284769180518, -7.043284769180518, -7.746346776498029, -7.746346776498029, -7.746346776498029, -7.746346776498029, -7.573201854333462, -7.573201854333462, -7.392876112547938, -7.392876112547938, -7.392876112547938, -7.392876112547938, -7.392876112547938, -7.392876112547938, -6.887898934559893, -6.887898934559893, -6.887898934559893, -6.60700246261079, -6.60700246261079, -6.60700246261079, -6.60700246261079, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.743904226310606, -6.361924822859237, -6.361924822859237, -6.361924822859237, -6.361924822859237, -6.361924822859237, -6.361924822859237, -6.361924822859237, -6.361924822859237, -6.361924822859237], [16.428689839572183, 16.428689839572183, 16.569314839572183, 13.401079545454538, 14.107025063351275, 14.107025063351275, 15.022443181818172, 14.11708603896103, 15.529586038961028, 14.120870442630755, 14.563548303111974, 14.45486307212058, 14.175924194476401, 15.108806818181808, 13.783124999999993, 13.783124999999993, 15.165624999999991, 15.165624999999991, 15.61562499999999, 15.61562499999999, 13.744106012658222, 13.744106012658222, 15.104945388349506, 15.104945388349506, 15.51817888940955, 15.51817888940955, 15.51817888940955, 15.51817888940955, 15.51817888940955, 15.51817888940955, 16.06562499999999, 16.06562499999999, 16.06562499999999, 16.06562499999999, 16.06562499999999, 16.06562499999999, 14.120378466872102, 14.120378466872102, 14.120378466872102, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 15.047918868921768, 15.047918868921768, 16.96562499999999, 16.96562499999999, 16.96562499999999, 16.96562499999999, 16.96562499999999, 16.96562499999999, 16.96562499999999, 16.96562499999999, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 14.551308699430242, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596, 15.219485523038596], [-8.843762904482052, -8.843762904482052, -9.014262904482052, -7.8063680195722105, -7.972408622755912, -7.791377247229145, -6.743071946222418, -5.925092636295978, -5.271183975350955, -4.936755652969658, -4.725593254970541, -4.520107107800931, -4.517652218939625, -4.360674223013261, -4.395151893697615, -4.395151893697615, -4.386197611212063, -4.373016294235162, -4.4290392755497265, -4.4290392755497265, -4.1105912668469164, -4.1105912668469164, -4.1219509791733255, -4.1219509791733255, -4.071781740534555, -4.071781740534555, -4.058575738400453, -4.058575738400453, -4.0609016209601405, -4.0609016209601405, -4.111549587836464, -4.078707895041818, -4.047096883000995, -4.046976380592243, -4.046976380592243, -4.046976380592243, -3.6321111078581074, -3.6321111078581074, -3.6321111078581074, -3.632241386029477, -3.633324230948251, -3.633324230948251, -3.633324230948251, -3.7836871892681, -3.7892725831676346, -3.7892725831676346, -3.829121299662918, -3.862716571110831, -3.868465888982058, -3.8892817749445814, -3.9332574148503685, -3.907288195987407, -3.8962106937178738, -3.902917217575517, -3.6807066790604472, -3.6807066790604472, -3.682658548940784, -3.682658548940784, -3.6990676991944746, -3.682658548940784, -3.682658548940784, -3.734876761179248, -3.734876761179248, -3.734876761179248, -3.734876761179248, -3.7318514447067144, -3.7318514447067144, -3.7782678813653905, -3.7782678813653905, -3.7782678813653905, -3.7782678813653905, -3.7782678813653905, -3.7782678813653905, -3.6139800946576885, -3.6139800946576885, -3.6139800946576885, -3.6374443450235416, -3.6374443450235416, -3.6374443450235416, -3.6374443450235416, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.6754968447089182, -3.575290043526362, -3.575290043526362, -3.575290043526362, -3.575290043526362, -3.575290043526362, -3.575290043526362, -3.575290043526362, -3.575290043526362, -3.575290043526362], [-1.6508858986793273, -1.6508858986793273, -1.6508858986793273, -1.9824632508063147, -0.7874834803963018, -0.7874834803963018, -0.7350351721256251, -0.8029038495008813, -0.6953030292684822, -1.170435168406639, -1.2101576493155606, -1.1593116349311345, -1.2809987688142075, -1.230697304260202, -2.2054923472500825, -2.2054923472500825, -1.679533280354093, -1.7471177810509915, -1.6921988948524442, -1.6921988948524442, -2.2555495252916047, -2.2555495252916047, -1.9160793891670815, -1.9160793891670815, -1.5380560396120297, -1.5380560396120297, -1.5380560396120297, -1.5380560396120297, -1.5380560396120297, -1.5380560396120297, -2.0188321174579715, -2.121896883218038, -2.2511656405295817, -2.2467786888985355, -2.2467786888985355, -2.2467786888985355, -1.7727781295460978, -1.7727781295460978, -1.7727781295460978, -1.7248833927039926, -1.3798833927039924, -1.3798833927039924, -1.3798833927039924, -1.4159030233416379, -1.5515547213829588, -1.5515547213829588, -2.490448958500519, -1.5898639664617453, -1.8828426853874582, -1.39711265296577, -0.7690261025739304, -0.6462639296698927, -1.0102565654638596, -0.6658021826373837, -0.6145814092495321, -0.6145814092495321, -0.38929569496381766, -0.38929569496381766, -0.2686664435508734, -0.38929569496381766, -0.38929569496381766, -0.10328990223809191, -0.10328990223809191, -0.10328990223809191, -0.10328990223809191, -0.06149940830614578, -0.06149940830614578, 0.07548464499702152, 0.07548464499702152, 0.07548464499702152, 0.07548464499702152, 0.07548464499702152, 0.07548464499702152, 0.08900874448013832, 0.08900874448013832, 0.08900874448013832, 0.3948366366905815, 0.3948366366905815, 0.3948366366905815, 0.3948366366905815, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.2793643070483677, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095, 0.44461433493189095]]
#
# acc = [[-12.211676658809832, -9.228145706321445, -9.929129861769542, -9.852078263619848, -8.657893569322567, -11.082629563587192, -12.615814992490222, -10.690673952619447, -10.847116372706212, -12.437060030254353, -10.847116372706212, -10.766494165013066, -10.766494165013066, -11.825141044898855, -10.670227845294434, -10.766494165013066, -11.70092881818962, -11.677740412392518, -11.770245863565151, -10.747943440375385, -12.447790127577615, -10.747943440375385, -10.837841010387372, -10.747943440375385, -10.847116372706212, -10.847116372706212, -10.847116372706212, -10.747943440375385, -10.747943440375385, -10.121491410940667, -10.747943440375385, -10.121491410940667, -10.517999924502757, -8.935709433302257, -9.715239673209805, -9.709698976323525, -9.278540207911202, -10.082928627722168, -9.278540207911202, -9.278540207911202, -9.278540207911202, -9.278540207911202, -10.46959063924372, -10.46959063924372, -10.831597565025165, -9.201784208274612, -10.831597565025165, -10.637872192688292, -10.637872192688292, -10.637872192688292], [5.815589232017569, 5.000345144960886, 4.794004206716073, 6.1595238095238125, 4.389365079365081, 4.207390737116767, 5.360126582278483, 5.191410853562755, 4.816410853562755, 4.421082251082253, 4.816410853562755, 4.820679146245683, 4.820679146245683, 5.19683982683983, 4.996839826839831, 4.820679146245683, 6.761320754716985, 6.761320754716985, 5.023843285995189, 4.820679146245683, 5.981284271284275, 4.820679146245683, 4.816410853562755, 4.820679146245683, 4.816410853562755, 4.816410853562755, 4.816410853562755, 4.820679146245683, 4.820679146245683, 4.996839826839831, 4.820679146245683, 4.996839826839831, 5.581284271284274, 4.824422677134545, 5.380724070450101, 5.208038901435131, 3.4441465703637295, 4.027003713220872, 3.4441465703637295, 3.4441465703637295, 3.4441465703637295, 3.4441465703637295, 4.422911065542648, 4.422911065542648, 4.602985785343394, 5.564285714285717, 4.602985785343394, 4.602985785343394, 4.602985785343394, 4.602985785343394], [-6.893829429002721, -6.229203385664119, -6.1476553413749215, -6.622072656311301, -6.293315662941137, -6.4201097015383715, -7.310379806036347, -8.279192613675606, -9.262000566405346, -6.971912578733314, -9.262000566405346, -9.388563769279747, -9.388563769279747, -7.228187277454135, -9.002527710578, -9.388563769279747, -9.618975575856144, -9.593702512585308, -9.621669362393186, -9.37908618803746, -9.580204865989547, -9.37908618803746, -9.249346628997143, -9.37908618803746, -9.262000566405346, -9.262000566405346, -9.262000566405346, -9.37908618803746, -9.37908618803746, -9.713941335267748, -9.37908618803746, -9.713941335267748, -9.860135446179651, -9.730623836813246, -8.039036026216383, -8.329627797262127, -8.44366971030446, -7.9432818938302905, -8.44366971030446, -8.44366971030446, -8.44366971030446, -8.44366971030446, -8.71686565596664, -8.71686565596664, -9.185597076405926, -8.848206473198086, -9.185597076405926, -10.15186100627468, -10.15186100627468, -10.15186100627468], [-2.356835372493334, -3.101947490591064, -2.698783640866553, -2.6995900924794562, -3.430238545764676, -2.678014750013703, -4.390322977562227, -3.344508622692018, -2.6024216463900363, -3.2561236683547623, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -2.9603163832321413, -3.344508622692018, -2.6024216463900363, -2.258561997267229, -2.258561997267229, -2.533311997267229, -2.6024216463900363, -3.4095099485329587, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -2.6024216463900363, -3.275398973569211, -2.6024216463900363, -3.275398973569211, -3.275398973569211, -3.058999203049306, -3.2856606962656048, -3.0830164420394524, -3.006732728974546, -3.0088755861174032, -3.006732728974546, -3.006732728974546, -3.006732728974546, -3.006732728974546, -3.261997227291442, -3.261997227291442, -2.9085725697571956, -4.023953986061103, -2.9085725697571956, -2.9085725697571956, -2.9085725697571956, -2.9085725697571956], []]
# ratio = [0.12, 0.08333333333333333, 0.0625, 0.061224489795918366, 0.1875, 0.2708333333333333, 0.3673469387755102, 0.47058823529411764, 0.52, 0.38, 0.52, 0.5, 0.5, 0.38, 0.46, 0.5, 0.52, 0.52, 0.5098039215686274, 0.5, 0.4807692307692308, 0.5, 0.52, 0.5, 0.52, 0.52, 0.52, 0.5, 0.5, 0.48, 0.5, 0.48, 0.48, 0.42, 0.375, 0.32653061224489793, 0.2653061224489796, 0.2857142857142857, 0.2653061224489796, 0.2653061224489796, 0.2653061224489796, 0.2653061224489796, 0.36, 0.36, 0.4, 0.375, 0.4, 0.46, 0.46, 0.46]
#
# acc = [[-3.8025700259768453, -2.6644705890763034, -2.688042017647732, -2.688042017647732, -2.2531464601250244, -2.688042017647732, -3.751811009262618, -3.751811009262618, -3.1529116264655324, -1.9510950484143854, -2.0413193739611297, -2.0413193739611297, -2.710767600713401, -2.661481886427686, -2.661481886427686, -3.214457531445074, -3.214457531445074, -3.214457531445074, -3.214457531445074, -3.214457531445074, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.2227470051292846, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.25658159159545, -3.153627194429784, -3.153627194429784, -3.153627194429784, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0976374575650425, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058, -3.0348742996703058], [14.320568181818174, 15.316484962406006, 15.316484962406006, 15.316484962406006, 15.726437132380589, 15.316484962406006, 15.087499999999991, 15.087499999999991, 15.753647393489157, 16.680674420516183, 14.86973171565276, 14.86973171565276, 14.423447340330894, 14.423447340330894, 14.423447340330894, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 14.880674420516184, 15.407889610389601, 15.407889610389601, 15.407889610389601, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848, 15.469642857142848], [-7.4758511826163625, -8.64593783982418, -8.561442410162323, -8.561442410162323, -9.82641815266965, -8.561442410162323, -6.565713615097793, -6.565713615097793, -8.851933542614832, -9.92507131240994, -8.699524762993802, -8.699524762993802, -9.256683727810863, -9.226812141199728, -9.226812141199728, -10.202898185866296, -10.202898185866296, -10.202898185866296, -10.202898185866296, -10.202898185866296, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.202110213350185, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -10.157922605981035, -9.264695384079722, -9.264695384079722, -9.264695384079722, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.892055287252964, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132, -8.886715299198132], [-0.6974964357955222, -0.19443578667820618, -0.200190262381531, -0.200190262381531, -0.1583984948270516, -0.200190262381531, -0.1122271505302293, -0.1122271505302293, 0.024498838019130373, -0.4956402530688098, -0.515426156908812, -0.515426156908812, -0.7677497708134117, -0.7735042465167365, -0.7735042465167365, -0.7193822710455771, -0.7193822710455771, -0.7193822710455771, -0.7193822710455771, -0.7193822710455771, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7242209807229965, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.7771657231126505, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.8257371516840791, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176, -0.7807192385627176], []]
# x = []
# for i in range(100):
#     x.append(i)
# # print("x", x)
# # print("a0", a[0])
# # print("a1", a[1])
# # print("a2", a[2])
# # print("a8", a[8])
# ln1, = plt.plot(x, acc[0], color='black', linewidth=1, linestyle=':')
# ln2, = plt.plot(x, acc[1], "black", linewidth=1, linestyle='-')
# ln3, = plt.plot(x, acc[2], "black", linewidth=1, linestyle='--')
# # ln4, = plt.plot(x, a[3], "cyan", linewidth=1)
# # ln5, = plt.plot(x, a[4], "purple", linewidth=1)
# # ln6, = plt.plot(x, a[5], 'pink', linewidth=1)
# # ln7, = plt.plot(x, a[6], "red", linewidth=1)
# # ln8, = plt.plot(x, a[7], "green", linewidth=1)
# ln9, = plt.plot(x, acc[3], "black", linewidth=1, linestyle='-.')
#
# plt.legend(handles=[ln1, ln2, ln3, ln9],
#            labels=['Node 1', 'Node 2', 'Node 3', 'Node 4'], loc="best", frameon=False)
# plt.rcParams['savefig.dpi'] = 300  # 图片像素
# plt.rcParams['figure.dpi'] = 1500  # 分辨率
# # plt.xticks(fontsize=20)#字体
# # plt.yticks(fontsize=20)
# plt.xlabel("Episode", fontsize=15)
# plt.ylabel("Accumulated reward", fontsize=15)
#
# plt.ylim(-20, 20)
# plt.xlim(0, 50)
#
# x_major_locator = MultipleLocator(10)
# y_major_locator = MultipleLocator(5)
# ax = plt.gca()
# ax.xaxis.set_major_locator(x_major_locator)
# ax.yaxis.set_major_locator(y_major_locator)
#
# plt.show()

# ratio = [0.12, 0.08333333333333333, 0.0625, 0.061224489795918366, 0.1875, 0.2708333333333333, 0.3673469387755102, 0.47058823529411764, 0.52, 0.38, 0.52, 0.5, 0.5, 0.38, 0.46, 0.5, 0.52, 0.52, 0.5098039215686274, 0.5, 0.4807692307692308, 0.5, 0.52, 0.5, 0.52, 0.52, 0.52, 0.5, 0.5, 0.48, 0.5, 0.48, 0.48, 0.42, 0.375, 0.32653061224489793, 0.2653061224489796, 0.2857142857142857, 0.2653061224489796, 0.2653061224489796, 0.2653061224489796, 0.2653061224489796, 0.36, 0.36, 0.4, 0.375, 0.4, 0.46, 0.46, 0.46]
# # ratio = [0.35294117647058826, 0.3333333333333333, 0.3333333333333333, 0.3333333333333333, 0.4230769230769231, 0.3333333333333333, 0.2857142857142857, 0.2857142857142857, 0.4230769230769231, 0.40384615384615385, 0.43137254901960786, 0.43137254901960786, 0.38, 0.38, 0.38, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.4117647058823529, 0.39215686274509803, 0.39215686274509803, 0.39215686274509803, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36, 0.36]
#
# x = []
# for i in range(50):
#     x.append(i)
#
# ln1, = plt.plot(x, ratio, color='black', linewidth=1, linestyle='-')
#
# # plt.legend(handles=[ln1],
# #            labels=['Node 1'], loc="upper right", frameon=False)
# plt.rcParams['savefig.dpi'] = 300  # 图片像素
# plt.rcParams['figure.dpi'] = 1500  # 分辨率
# # plt.xticks(fontsize=20)#字体
# # plt.yticks(fontsize=20)
# plt.xlabel("Episode", fontsize=15)
# plt.ylabel("Ratio of delay satisfied reqs to all reqs", fontsize=15)
#
# plt.ylim(0, 1)
# plt.xlim(0, 50)
#
# x_major_locator = MultipleLocator(10)
# y_major_locator = MultipleLocator(0.1)
# ax = plt.gca()
# ax.xaxis.set_major_locator(x_major_locator)
# ax.yaxis.set_major_locator(y_major_locator)
#
# plt.show()
