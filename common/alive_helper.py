import threading
import re


class AliveHelper(threading.Thread):

    def __init__(self):
        super().__init__()
        self.alive = True
        self.start()

    def run(self):
        while re.match(r"^[Yy](?:es|ES)?$", input('end?>')) is None:
            pass
        self.alive = False
