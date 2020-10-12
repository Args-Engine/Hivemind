import select
import socket
import threading
from typing import List

from common.application_params import PORT, MAX_MSG_LEN
from common.message_frame import MessageFrame
from messages.ping import Ping
from server.middleware import Middleware


class Server(threading.Thread):
    def __init__(self, middleware: Middleware):
        super().__init__()

        self.keep_alive = True
        self.initialized = False

        self.socket: socket = None
        self.read_list: List[socket] = []
        self.middleware = middleware

    def initialize_socket(self):

        # create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

        # bind and listen to socket
        server_addr = ("0.0.0.0", PORT)
        print("Starting to listen on %s:%s" % server_addr)
        self.socket.bind(server_addr)
        self.socket.listen(5)
        self.read_list += [self.socket]
        self.initialized = True

    def run(self):
        # init then run
        if not self.initialized:
            self.initialize_socket()
        while self.keep_alive:
            self.communicate()

    def communicate(self) -> None:

        # check if initialization occurred
        if not self.initialized:
            raise Exception("Socket was not initialized")

        # check if the socket timed out
        for sock in self.read_list:
            if sock is self.socket:
                continue

            # ask the middleware if this session timed out
            if self.middleware.check(sock):
                self.read_list.remove(sock)

        readable, writeable, exceptional = select.select(self.read_list, [], [], 10)
        for sock in readable:
            if sock is self.socket:

                # Connect new peer
                client_sock, addr = self.socket.accept()
                self.read_list.append(client_sock)
                self.middleware.connect_event(self.socket)
            else:

                try:
                    # receive Data
                    data = sock.recv(MAX_MSG_LEN)
                except (ConnectionResetError, ConnectionAbortedError):

                    # Connection Terminated
                    print("Bad peer, disconnected")
                    self.read_list.remove(sock)
                    self.middleware.remove(sock)
                    continue

                # Construct frame from raw data
                frame = MessageFrame()
                frame.decode(data)

                # check if there is messages in the frame
                while frame.available():
                    message = frame.get_message()
                    self.middleware.ingest(sock, message)

                # craft frame with our own messages
                frame = MessageFrame()
                while self.middleware.has_message_for(sock):
                    frame.add_message(self.middleware.emit(sock))

                # Make sure it isn't completely empty
                if frame.empty():
                    frame.add_message(Ping())

                try:
                    # Send our response
                    sock.send(frame.encode())
                except (ConnectionResetError, ConnectionAbortedError):

                    # Connection Terminated
                    print("Bad peer, disconnected")
                    self.read_list.remove(sock)
                    self.middleware.remove(sock)
                    continue


