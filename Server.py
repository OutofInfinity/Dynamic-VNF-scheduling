import Environment1
import Environment3
# import Environment4
import Environment5
import Environment0
import Environment2_
import Environment2

class Server:
    rSize = Environment2.rSize
    handle: int

    def __init__(self):
        self.handle = 0
        self.task = []
        self.come = []
        self.come_delay = []
        self.task_delay = []
        self.finish_delay = []
        self.total = 0

    # receive new requests
    def receive(self, c, d):
        self.come = []
        self.come_delay = []
        for i in range(len(c)):
            self.come.append(c[i])
            self.come_delay.append(d[i])

        # import new come
        while self.handle < self.rSize and self.come:
            self.task.append(self.come[0])
            self.task_delay.append(self.come_delay[0])
            self.handle += 1
            self.total += 1
            del self.come[0]
            del self.come_delay[0]

    # collect from nodes
    def collect(self, r, d):
        if r == [-1, -1]:
            self.handle -= 1
            self.finish_delay.append(d)
        else:
            if r:
                self.task.append(r)
                self.task_delay.append(d)

    # send
    def send(self):
        return self.task.pop(0)

    # send delay
    def send_delay(self):
        return self.task_delay.pop(0)

    def send_finish_delay(self):
        return self.finish_delay

    def clear_finish_delay(self):
        self.finish_delay.clear()

    def clear(self):
        self.handle = 0
        self.task.clear()
        self.come = []
        self.come_delay = []
        self.task_delay = []
        self.finish_delay = []
        self.total = 0
