from multiprocessing import cpu_count
from queue import Queue
from typing import NoReturn, Union, List, Tuple, Dict

from client.modules.dispatcher_runner import Runner
from common.module_base import ModuleBase
from common.session_base import SessionBase
from messages import Tasks, Ping, AvailableCores


class DispatcherModule(ModuleBase):

    def __init__(self):
        super().__init__(["Tasks", "Ping"])

        self.task_queue: Queue[Tuple[str, str]] = Queue()
        self.genesis_not_sent = True
        self.runners: List[Runner] = []
        self.in_use = 0
        self.finished_tasks_per_workspace: Queue[str] = Queue()

    def handle(self, message_name: str, message_value: Union[Tasks, Ping], session: SessionBase) -> NoReturn:

        # check if a ping as sent and if this is the first ping we received
        if message_name == "Ping" and self.genesis_not_sent:
            self.genesis_not_sent = False

            # if so send how many cores are available
            session.to_send.put(AvailableCores(available=cpu_count(), per_workspace={}))

        # check if we received tasks from the server
        if message_name == "Tasks":

            # get all tasks out of the message and put them in the queue
            for task in message_value.tasks:
                self.task_queue.put(task)

            finished: Dict[str, int] = {}

            # check how many tasks per workspace have finished
            while not self.finished_tasks_per_workspace.empty():
                workspace = self.finished_tasks_per_workspace.get()
                if workspace not in finished:
                    finished[workspace] = 1
                finished[workspace] += 1

            # respond with how many cores we will have available after scheduling these tasks
            session.to_send.put(
                AvailableCores(available=cpu_count() - self.task_queue.qsize(), per_workspace=finished))

    def onUpdate(self):

        # run as many tasks as we can
        while not self.in_use >= cpu_count() and not self.task_queue.empty():
            self.in_use += 1

            # run the task if cpu cores are available & tasks are available
            (command, workspace) = self.task_queue.get()
            self.runners.append(Runner(command, workspace))

        # check if some runners already finished
        for runner in self.runners:
            if runner.done():
                self.finished_tasks_per_workspace.put(runner.workspace)
                self.in_use -= 1
                self.runners.remove(runner)
