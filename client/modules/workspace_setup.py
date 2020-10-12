import os
import shutil
from typing import NoReturn, Union

from client.session import Session
from common.module_base import ModuleBase
from common.share_helper import share_drive_letter
from common.update_returns import EmitError
from messages import ExecutionRequest, ExecutionDone, ExecutionResponse
from messages.workspace_response import WorkspaceResponse


class WorkspaceSetup(ModuleBase):

    def __init__(self):
        super().__init__(["WorkspaceResponse",
                          "ExecutionResponse",
                          "ExecutionDone"])

    def handle(self, message_name: str, message_value: Union[WorkspaceResponse, ExecutionResponse, ExecutionDone],
               session: Session) -> NoReturn:

        if message_name == "WorkspaceResponse":

            if 'workspace-base-path' in session:
                base_dir = session['workspace-base-path']
                print(base_dir)
                print(os.path.join(share_drive_letter +"/" , message_value.workspace)+"/")
                shutil.copytree(base_dir, os.path.join(share_drive_letter +"/" , message_value.workspace)+"/",dirs_exist_ok=True)
                if 'workspaces' not in session:
                    session['workspaces'] = {message_value.workspace: base_dir}

                try:
                    print(os.path.join(base_dir, "hivemind.txt"))
                    with open(os.path.join(base_dir, "hivemind.txt"), "r") as file:
                        tasks = file.readlines()
                        session.to_send.put(ExecutionRequest(tasks, message_value.workspace))

                except FileNotFoundError:
                    print("error opening file")
                    return EmitError("Error: directory is invalid! Does not contain hivemind.txt")

            else:
                return EmitError("Error: received workspace response without active workspace location")

        if message_name == "ExecutionResponse":
            if not message_value.accepted:
                return EmitError("Server refused execution of our script!")

        if message_name == "ExecutionDone":
            output_dir = session['workspaces'][message_value.workspace] + '_finished'

            os.makedirs(output_dir, exist_ok=True)

            shutil.copytree(os.path.join(share_drive_letter, message_value.workspace),
                            output_dir)

