from queue import Queue

# base class for both the server & the client session
# TODO(algo-ryth-mix): This should probably have the __get/setitem__ that both sessions have
class SessionBase:
    def __init__(self):
        self.to_send = Queue()
