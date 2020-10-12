from typing import NoReturn

from client.session import Session
from common.module_base import ModuleBase
from common.share_helper import NetShareConnect
from common.update_returns import EmitError
from messages import WorkspaceConnect


class ShareConnector(ModuleBase):

    def __init__(self):
        super().__init__(["WorkspaceConnect"])
        self.connected = False

    def handle(self, message_name: str, message_value: WorkspaceConnect,
               session: Session) -> NoReturn:

        if message_name == "WorkspaceConnect" and self.connected is not True:
            print("Attempting to connect")
            if NetShareConnect(message_value.share_name, message_value.user, message_value.password) is False:
                print("Failed to connect")
            else:
                print("Connected to Remote")
                self.connected = True
        elif self.connected is True:
            print("Server keeps trying to connect us, dunno why")