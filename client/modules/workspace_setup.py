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

                # local and remote directories
                base_dir = session['workspace-base-path']
                network_dir = os.path.join(share_drive_letter + "/", message_value.workspace) + "/"

                print("Received Workspace: " + network_dir)

                # copy files to remote
                shutil.copytree(base_dir, network_dir, dirs_exist_ok=True)

                # create workspaces field
                if 'workspaces' not in session:
                    session['workspaces'] = {message_value.workspace: base_dir}

                # open instructions file & send to server
                try:
                    with open(os.path.join(base_dir, "hivemind.txt"), "r") as file:
                        tasks = file.readlines()
                        session.to_send.put(ExecutionRequest(tasks, message_value.workspace))

                except FileNotFoundError:
                    print("error opening file")
                    return EmitError("Error: directory is invalid! Does not contain hivemind.txt")

            else:
                return EmitError("Error: received workspace response without active workspace location")

        if message_name == "ExecutionResponse":
            # inform the user if the server refused execution

            if not message_value.accepted:
                return EmitError("Server refused execution of our script!")

        if message_name == "ExecutionDone":
            print(f"Environment {session['workspaces'][message_value.workspace]} done")

            # make output folder
            output_dir = session['workspaces'][message_value.workspace] + '_finished'
            os.makedirs(output_dir, exist_ok=True)

            # copy remote to local folder
            shutil.copytree(os.path.join(share_drive_letter, message_value.workspace),
                            output_dir, dirs_exist_ok=True)
