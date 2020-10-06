from typing import List


class ExecutionRequest:
    def __init__(self, tasklist: List[str], workspace):
        self.tasklist = tasklist
        self.workspace = workspace
