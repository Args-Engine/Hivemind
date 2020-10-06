from queue import Queue


class SessionBase:
    def __init__(self):
        self.to_send = Queue()
