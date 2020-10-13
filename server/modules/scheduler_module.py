from queue import Queue
from typing import NoReturn, Dict, Union, Tuple

from common.module_base import ModuleBase
from messages import Tasks, AvailableCores
from messages.execution_done import ExecutionDone
from messages.execution_request import ExecutionRequest
from messages.execution_response import ExecutionResponse
from server.layout.workspace_layout import Workspace, parse_instructions
from server.session import Session

class SchedulerModule(ModuleBase):

    def __init__(self):
        super().__init__(["AvailableCores",
                          "ExecutionRequest"])
        self.workspaces: Dict[str, Workspace] = {}

    def handle(self, message_name: str, message_value: Union[AvailableCores, ExecutionRequest],
               session: Session) -> NoReturn:

        # a client reported how many cores it has available
        if message_name == "AvailableCores":

            # check the per workspace finishes
            for workspace_id, finished in message_value.per_workspace.items():

                # get the workspace the runner worked for
                workspace = self.workspaces.get(workspace_id, None)
                if workspace is not None:
                    # return tasks to the workspace
                    workspace.task_returned(finished)

                else:
                    print("Warning, this runner worked for a workspace that does not exist on the server")

            # check if we have seen this client before
            # otherwise register how many cpus it has
            if 'cpu_count' in session:
                session['cpu_count'] = message_value.available

            # update the available cpus this client has
            session['cpu_available'] = message_value.available

            tasks = []

            # check how many tasks to send (may be empty!)
            tasks_to_get = session['cpu_available']

            # generate task lists with tasks from all workspaces
            for workspace_id, workspace in self.workspaces.items():
                while workspace.can_get_next() and tasks_to_get != 0:
                    task = workspace.get_next()
                    tasks += [(task.payload, workspace_id, task.unique_identifier)]

            # make sure we don't have any ghost-workspaces
            for workspace_id, workspace in self.workspaces.items():
                if workspace.destroy_on_sight:
                    del workspace

            # send tasks
            session.to_send.put(Tasks(tasks))

        if message_name == "ExecutionRequest":
            # Get all tasks and put them in the queue of the workspace
            instructions = parse_instructions(message_value.tasklist)

            # create a new workspace session for the client
            self.workspaces[message_value.workspace] = Workspace(session, instructions)

            # respond that we accepted the execution request
            session.to_send.put(ExecutionResponse(accepted=True))

    def onUpdate(self):
        for workspace_id, workspace in self.workspaces.items():

            # make really(!) sure that the workspace is done
            if not workspace.can_get_next() and not workspace.blocked() and not workspace.destroy_on_sight and \
                    len(workspace.current_running) == 0:

                print(f"Workspace {workspace_id} needs to stop!")

                # send the client the response that its environment is done
                workspace.session.to_send.put(ExecutionDone(workspace=workspace_id))

                # mark it for destruction
                workspace.destroy_on_sight = True
