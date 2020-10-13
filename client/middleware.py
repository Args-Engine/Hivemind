from socket import socket

from client.session import Session
from common.module_base import ModuleBase
from typing import List

from common.update_returns import ApplicationExit , EmitError
from messages import msg_name_table


class Middleware:

    def __init__(self, modules: List[ModuleBase], addr="localhost"):
        self.should_close = False
        self.modules = modules
        self.session = Session()
        self.addr = addr

        for module in modules:
            if getattr(module, 'onRegister', None) is not None and callable(module.onRegister):
                module.onRegister(modules, self)

    # inform modules that we connected to a server
    def connect_event(self, _: socket):
        for module in self.modules:
            if getattr(module, 'onConnect', None) is not None and callable(module.onConnect):
                module.onConnect(self.session)

    # check if a message is available
    def has_message(self):
        return not self.session.to_send.empty()

    # get a message from the Queue
    def emit(self):
        return self.session.to_send.get()

    # receive messages from the server
    def ingest(self, message):

        # check if we support that message
        name = msg_name_table.get(type(message))
        if name is None:
            raise Exception("This Message is not supported! ", message)

        # check if anyone is interested in the message
        for module in self.modules:
            if name in module.interests or type(message) in module.interests:
                module.handle(name, message, self.session)

    def update(self) -> bool:

        # update each modules, watching out for ApplicationExists and EmitErrors
        for module in self.modules:
            if getattr(module, 'onUpdate', None) is not None and callable(module.onUpdate):
                response = module.onUpdate()
                if type(response) is ApplicationExit:
                    return False
                elif type(response) is EmitError:
                    print(response.error)

        return True
