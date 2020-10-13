from typing import NoReturn

from client.session import Session
from common.module_base import ModuleBase
from common.share_helper import NetShareConnect
from messages import WorkspaceConnect


class ShareConnector(ModuleBase):

    def __init__(self):
        super().__init__(["WorkspaceConnect"])
        self.connected = False

    def handle(self, message_name: str, message_value: WorkspaceConnect,
               session: Session) -> NoReturn:

        # check if we already are connected
        if message_name == "WorkspaceConnect" and self.connected is not True:
            print("Attempting to connect")

            # do some evil things
            if NetShareConnect(message_value.share_name, message_value.user, message_value.password):
                print("Connected to Remote")
                self.connected = True
            else:
                print("Failed to connect")

        # confusion intensifies ? Server already told us to connect once
        elif self.connected is True:
            print("Server keeps trying to connect us, dunno why")
