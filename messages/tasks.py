from typing import List, Tuple


class Tasks:

    # tasks is a list of task to run + workspace to run in
    def __init__(self, tasks: List[Tuple[str, str]]):
        self.tasks = tasks
