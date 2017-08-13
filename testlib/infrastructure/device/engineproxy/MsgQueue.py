import Queue


class MsgQueue(Queue.Queue):
    def __init__(self):
        Queue.Queue.__init__(self)

    def add_msg(self, msg):
        self.put(msg)

    def get_msg(self):
        # if self.qsize() > 0:
        #     return self.get()
        return self.get(True)
