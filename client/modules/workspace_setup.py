from typing import NoReturn, Union

from common.module_base import ModuleBase
from common.session_base import SessionBase
from common.update_returns import EmitError
from common.share_helper import NetShareConnect
from messages.workspace_response import WorkspaceResponse
from messages.workspace_connect  import WorkspaceConnect

class WorkspaceSetup(ModuleBase):

    def __init__(self):
        super().__init__(["WorkspaceResponse","WorkspaceConnect"])
        self.connected = False

    def handle(self, message_name: str, message_value :Union[WorkspaceResponse,WorkspaceConnect], session: SessionBase) -> NoReturn:


        if message_name == "WorkspaceConnect" and self.connected is not True:
            if 'workspace-base-path' in session:
                print("Attempting to connect")
                if NetShareConnect(message_value.share_name,message_value.user,message_value.password) is False:
                    print("Failed to connect")
                else:
                    print("Connected to Remote")
                    self.connected = True
            else:
                return EmitError("Error, received workspace response without active workspace location")
        elif self.connected is True:
            print("Server keeps trying to connect us, dunno why")
        else:
            print(f"Received response for workspace {message_value.workspace}")