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

        self.task_queue: Queue[Tuple[str, str, str]] = Queue()
        self.runners: List[Runner] = []
        self.in_use = 0
        self.finished_tasks_per_workspace: Queue[Tuple[str,str]] = Queue()


    def onConnect(self, session: SessionBase):

        # inform the server about how many cores we have
        session.to_send.put(AvailableCores(available=cpu_count(), per_workspace={}))

    def handle(self, message_name: str, message_value: Union[Tasks, Ping], session: SessionBase) -> NoReturn:

        # check if we received tasks from the server
        if message_name == "Tasks":

            # get all tasks out of the message and put them in the queue
            for task in message_value.tasks:
                self.task_queue.put(task)

            finished: Dict[str, List[str]] = {}

            # check how many tasks per workspace have finished
            while not self.finished_tasks_per_workspace.empty():
                (workspace, uid) = self.finished_tasks_per_workspace.get()
                if workspace not in finished:
                    finished[workspace] = [uid]
                finished[workspace] += [uid]

            # respond with how many cores we will have available after scheduling these tasks
            session.to_send.put(
                AvailableCores(available=cpu_count() - self.task_queue.qsize(), per_workspace=finished))

    def onUpdate(self):

        # run as many tasks as we can
        while not self.in_use >= cpu_count() and not self.task_queue.empty():
            self.in_use += 1

            # run the task if cpu cores are available & tasks are available
            (command, workspace, uid) = self.task_queue.get()
            self.runners.append(Runner(command, workspace, uid))

        # check if some runners already finished
        for runner in self.runners:
            if runner.done():
                self.finished_tasks_per_workspace.put((runner.workspace,runner.uid))
                self.in_use -= 1
                self.runners.remove(runner)
