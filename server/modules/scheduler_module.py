from queue import Queue
from typing import NoReturn, Dict, Union, Tuple

from common.module_base import ModuleBase
from messages import Tasks, AvailableCores
from messages.execution_done import ExecutionDone
from messages.execution_request import ExecutionRequest
from messages.execution_response import ExecutionResponse
from server.session import Session


class SchedulerModule(ModuleBase):

    def __init__(self):
        super().__init__()
        self.interests = ["AvailableCores",
                          "ExecutionRequest"]
        self.tasks: Queue[Tuple[str, str]] = Queue()
        self.max_cpus = 0

        self.workspaces: Dict[str, Tuple[Session, int]] = {}

    def handle(self, message_name: str, message_value: Union[AvailableCores, ExecutionRequest],
               session: Session) -> NoReturn:

        # a client reported how many cores it has available
        if message_name == "AvailableCores":

            # check the per workspace finishes
            for workspace, finished in message_value.per_workspace.items():

                # get the workspace the runner worked for
                data = self.workspaces.get(workspace, None)
                if data is not None:

                    # extract the data
                    session, to_execute = data
                    to_execute -= finished

                    # check if the workspace is done
                    if to_execute <= 0:

                        # send the finish signal to the session of this workspace &
                        # delete the workspace
                        session.to_send.put(ExecutionDone())
                        del self.workspaces[workspace]
                    else:

                        # re-insert the workspace with the updated parameters
                        self.workspaces[workspace] = (session, to_execute)

                else:
                    print("Warning, this runner worked for a workspace that does not exist on the server")

            # check if we have seen this client before
            # otherwise register how many cpus it has
            if 'cpu_count' in session:
                session['cpu_count'] = message_value.available
                self.max_cpus += message_value.available

            # update the available cpus this client has
            session['cpu_available'] = message_value.available

            # check how many tasks to send (may be empty!)
            max_avail = min(session['cpu_available'], self.tasks.qsize())

            # generate task list
            tasks = [self.tasks.get() for _ in range(0, max_avail)]

            # send tasks
            session.to_send.put(Tasks(tasks))

        if message_name == "ExecutionRequest":

            # Get all tasks and put them in the queue
            for task in message_value.tasklist:
                self.tasks.put((task, message_value.workspace))

            # create a new workspace session for the client
            self.workspaces[message_value.workspace] = (session, len(message_value.tasklist))

            # respond that we accepted the execution request
            session.to_send.put(ExecutionResponse(accepted=True))
