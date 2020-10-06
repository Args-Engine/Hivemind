from datetime import datetime
from socket import socket
from typing import List, Dict, Any, NoReturn

from messages import msg_name_table, Ping
from common.module_base import ModuleBase
from server.session import Session


class Middleware:

    def __init__(self, modules: List[ModuleBase]):
        self.sessions: Dict[socket, Session] = {}
        self.modules = modules

    def has_message_for(self, session_key: socket) -> bool:

        session = self.sessions.get(session_key)
        if session is not None:
            return session.to_send.qsize() > 0
        else:
            return False

    def emit(self, session_key: socket) -> Any:
        session = self.sessions.get(session_key)
        if session is not None:
            return session.to_send.get()
        else:
            raise Exception("Attempted to get a Message for a Session that does not exist")

    def ingest(self, session_key: socket, message) -> NoReturn:

        # generate a new session if needed
        if session_key not in self.sessions:
            self.sessions[session_key] = Session()

        session = self.sessions[session_key]

        session.last_seen = datetime.now()

        # check if we support that message
        name = msg_name_table.get(type(message))

        if name is None:
            print(type(message), Ping)
            raise Exception("This Message is not supported! ", message)

        # check if anyone is interested in the message
        for module in self.modules:
            if name in module.interests:
                module.handle(name, message, session)

    def check(self, session_key: socket) -> bool:

        if session_key not in self.sessions:
            return False

        # check if the session expired
        now = datetime.now()
        if (now - self.sessions[session_key].last_seen).seconds > 5:
            self.remove(session_key)
            return True

        return False

    def remove(self, session_key: socket) -> NoReturn:
        self.sessions.pop(session_key)

    def update(self):
        for module in self.modules:
            if getattr(module, 'onUpdate', None) is not None and callable(module.onUpdate):
                module.onUpdate()
