from client.session import Session
from common.module_base import ModuleBase
from typing import List

from messages import msg_name_table


class Middleware:

    def __init__(self, modules: List[ModuleBase], addr="localhost"):
        self.should_close = False
        self.modules = modules
        self.session = Session()
        self.addr = addr

    def has_message(self):
        return self.session.to_send.qsize() > 0

    def emit(self):
        return self.session.to_send.get()

    def ingest(self, message):

        # check if we support that message
        name = msg_name_table.get(type(message))
        if name is None:
            raise Exception("This Message is not supported! ", message)

        # check if anyone is interested in the message
        for module in self.modules:
            if name in module.interests or type(message) in module.interests:
                module.handle(name, message, self.session)

    def update(self):
        for module in self.modules:
            if getattr(module, 'onUpdate', None) is not None and callable(module.onUpdate):
                module.onUpdate()
        pass
