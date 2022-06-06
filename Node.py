import random
import torchNN_Agent

# PHI1 = torchNN_Agent.PHI1
# PHI2 = torchNN_Agent.PHI2
# PHI3 = torchNN_Agent.PHI3
PHI1 = 0.45
PHI2 = 0.45
PHI3 = 0.1


class Node:

    def __init__(self):
        self.processing = -1
        self.queue = []
        self.finish = []
        self.finish_delay = -1
        self.delay = []
        self.m_delay = []
        self.wait = []
        self.t = 0

    def clear(self):
        self.processing = -1
        self.queue = []
        self.finish = []
        self.finish_delay = -1
        self.delay = []
        self.wait = []

    def receive(self, r, d):
        self.queue.append(r)
        self.delay.append(d)
        self.wait.append(0)

    def random_decide(self):
        decision = random.randint(0, len(self.queue) - 1)
        self.processing = decision

    def set_processing(self, d):
        self.processing = d


    def delay_greedy(self):
        min_delay = self.delay[0]
        decision = 0
        for i in range(len(self.delay)):
            if self.delay[i] < min_delay:
                min_delay = self.delay[i]
                decision = i
        self.processing = decision


    def vnf_num_greedy(self):
        min_num = len(self.queue[0])
        decision = 0
        for i in range(len(self.queue)):
            if len(self.queue[i]) < min_num:
                min_num = len(self.queue[i])
                decision = i
        self.processing = decision


    def wait_greedy(self):
        max_wait = self.wait[0]
        decision = 0
        for i in range(len(self.wait)):
            if self.wait[i] > max_wait:
                max_wait = self.wait[i]
                decision = i
        self.processing = decision

    def quick_transition(self, rt):
        diff = rt - self.t
        self.finish = []
        self.finish_delay = -1
        # print(self.delay, self.processing)
        # if there is any request in queue
        if self.queue:
            # make a decision if it is idle
            if self.processing == -1:
                self.random_decide()
            # processing
            if self.processing != -1:
                self.queue[self.processing][0][1] -= diff
                for j in range(len(self.queue)):
                    if j != self.processing:
                        self.wait[j] += diff
                # VNF is finished
                if self.queue[self.processing][0][1] <= 0:
                    del self.queue[self.processing][0]
                    if self.queue[self.processing]:
                        self.finish = self.queue[self.processing]
                        self.finish_delay = self.delay[self.processing]
                        del self.queue[self.processing]
                        del self.delay[self.processing]
                        del self.wait[self.processing]
                    # whole request is finished
                    else:
                        self.finish = [-1, -1]
                        self.finish_delay = self.delay[self.processing]
                        del self.queue[self.processing]
                        del self.delay[self.processing]
                        del self.wait[self.processing]
                    # become idle
                    self.processing = -1
        else:
            self.processing = -1

    def transition(self):
        self.finish = []
        self.finish_delay = -1
        # print(self.delay, self.processing)
        # if there is any request in queue
        if self.queue:
            # make a decision if it is idle
            # if self.processing == -1:
            #     self.vnf_num_greedy()
            # processing
            if self.processing != -1:
                self.queue[self.processing][0][1] -= 1
                for j in range(len(self.queue)):
                    if j != self.processing:
                        self.wait[j] += 1
                # VNF is finished
                if self.queue[self.processing][0][1] == 0:
                    del self.queue[self.processing][0]
                    if self.queue[self.processing]:
                        self.finish = self.queue[self.processing]
                        self.finish_delay = self.delay[self.processing]
                        del self.queue[self.processing]
                        del self.delay[self.processing]
                        del self.wait[self.processing]
                    # whole request is finished
                    else:
                        self.finish = [-1, -1]
                        self.finish_delay = self.delay[self.processing]
                        del self.queue[self.processing]
                        del self.delay[self.processing]
                        del self.wait[self.processing]
                    # become idle
                    self.processing = -1
        else:
            self.processing = -1

    def send(self):
        return self.finish

    def send_delay(self):
        return self.finish_delay

    def count_reward(self, t):
        first = 0
        if self.finish == [-1, -1]:
            if t <= self.finish_delay:
                first = 1
        d_sum = 0
        ddl_sum = 0
        over = 0
        for i in range(len(self.delay)):
            d_sum += self.delay[i] - t - 1
            ddl_sum += self.delay[i]
            if t + 1 - self.delay[i] < 0:
                over += 1
        if ddl_sum == 0:
            second = 1
        else:
            second = d_sum / ddl_sum
        if len(self.delay) == 0:
            third = 0
        else:
            third = over / len(self.delay)

        r = PHI1 * first + PHI2 * second - PHI3 * third

        return r
