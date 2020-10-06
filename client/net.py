import socket
import threading

from client.middleware import Middleware
from common.application_params import PORT, MAX_MSG_LEN
from common.message_frame import MessageFrame
from messages import Ping


class Client(threading.Thread):
    def __init__(self, middleware: Middleware):
        super().__init__()
        self.middleware = middleware

        self.keep_alive = True
        self.initialized = False
        self.sock: socket = None

        self.established = False

    def initialize_socket(self):

        # create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # attempt to connect socket repeatedly
        while self.sock.connect_ex((self.middleware.addr, PORT)) != 0 and self.keep_alive:
            print("Connection failed, host not up!")

        self.initialized = True

    def run(self):
        # check if initialized and run client
        if not self.initialized:
            self.initialize_socket()
        while self.keep_alive:
            self.communicate()

    def communicate(self) -> None:

        # quit if initialization did not occur
        if not self.initialized:
            raise Exception("Client Socket has not been initialized")

        # check if the middleware instructed to quit
        if self.middleware.should_close:
            self.keep_alive = False

        # generate a new frame from the Middlewares messages
        frame = MessageFrame()
        while self.middleware.has_message():
            message = self.middleware.emit()
            frame.add_message(message)

        # make sure that the frame is not empty
        if frame.empty():
            frame.add_message(Ping())

        # send the frame
        self.sock.send(frame.encode())

        # receive response
        data = self.sock.recv(MAX_MSG_LEN)

        # decode response into frame
        frame = MessageFrame()
        frame.decode(data)

        # read all messages from the frame and inform the middleware about them
        while frame.available():
            message = frame.get_message()
            self.middleware.ingest(message)
