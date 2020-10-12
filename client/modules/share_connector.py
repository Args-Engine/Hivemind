from typing import NoReturn

from client.session import Session
from common.module_base import ModuleBase
from messages import WorkspaceConnect
from common.share_helper import NetShareConnect


class ShareConnector(ModuleBase):

    def __init__(self):
        super().__init__(["WorkspaceConnect"])
        self.connected = False

    def handle(self, message_name: str, message_value: WorkspaceConnect, session: Session) -> NoReturn:
        connection = NetShareConnect(message_value.share_name, message_value.user, message_value.password)
        self.connected = connection
