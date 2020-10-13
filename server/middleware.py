from datetime import datetime
from socket import socket
from typing import List, Dict, Any, NoReturn

from common.update_returns import ApplicationExit
from messages import msg_name_table, Ping
from common.module_base import ModuleBase
from server.session import Session


class Middleware:

    def __init__(self, modules: List[ModuleBase]):
        self.sessions: Dict[socket, Session] = {}
        self.modules = modules

        # invoke registration function, that allows modules to meet each other
        for module in modules:
            if getattr(module, 'onRegister', None) is not None and callable(module.onRegister):
                module.onRegister(modules, self)

    def connect_event(self, session_key: socket):
        if session_key not in self.sessions:
            self.sessions[session_key] = Session()

        # inform modules that want to know if a client connects
        for module in self.modules:
            if getattr(module, 'onConnect', None) is not None and callable(module.onConnect):
                module.onConnect(self.sessions[session_key])

    # check if a message for a session is available
    def has_message_for(self, session_key: socket) -> bool:

        session = self.sessions.get(session_key)
        if session is not None:
            return session.to_send.qsize() > 0
        else:
            return False

    # emit message for session
    def emit(self, session_key: socket) -> Any:
        session = self.sessions.get(session_key)
        if session is not None:
            return session.to_send.get()
        else:
            raise Exception("Attempted to get a Message for a Session that does not exist")

    # consume message from server for client
    def ingest(self, session_key: socket, message) -> NoReturn:

        # generate a new session if needed
        if session_key not in self.sessions:
            self.sessions[session_key] = Session()

        session = self.sessions[session_key]

        session.last_seen = datetime.now()

        # check if we support that message
        name = msg_name_table.get(type(message))

        # A message needs to be registered to be supported
        # TODO(algo-ryth-mix): is this check really required ?
        if name is None:
            print(type(message), Ping)
            raise Exception("This Message is not supported! ", message)

        # check if anyone is interested in the message
        for module in self.modules:
            if name in module.interests:
                module.handle(name, message, session)

    # check if a session expired
    def check(self, session_key: socket) -> bool:

        if session_key not in self.sessions:
            return False

        # check if the session expired
        now = datetime.now()
        if (now - self.sessions[session_key].last_seen).seconds > 5:
            self.remove(session_key)
            return True

        return False

    # remove a session
    def remove(self, session_key: socket) -> NoReturn:
        self.sessions.pop(session_key)

    # update modules
    def update(self) -> bool:
        for module in self.modules:
            if getattr(module, 'onUpdate', None) is not None and callable(module.onUpdate):
                if type(module.onUpdate()) is ApplicationExit:
                    return False

        return True
