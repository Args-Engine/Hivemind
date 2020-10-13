from collections import deque
from enum import Enum
from queue import Queue
from typing import List, Tuple, Union, Set

from client.session import Session
from uuid import uuid4

class Instruction:
    class Type(Enum):
        WAIT = 1
        RUN = 2

    def __init__(self, instruction_type: Type, payload: str, unique_identifier):
        self.instruction_type = instruction_type
        self.payload = payload
        self.unique_identifier = unique_identifier


class Workspace:
    def __init__(self, session: Session, tasks: List[Instruction]):
        self.tasks: Queue[Instruction] = Queue()
        self.tasks.queue = deque(tasks)
        self.current_running: Set[str] = set([])
        self.session = session
        self.destroy_on_sight = False

    def get_next(self) -> Union[Instruction, None]:

        task = None

        if self.can_get_next():
            while True:
                if self.tasks.empty():
                    break

                task = self.tasks.get()
                if task.instruction_type != Instruction.Type.WAIT:
                    self.current_running.add(task.unique_identifier)
                    break

        return task

    def task_returned(self, uids: List[str]):
        self.current_running.difference_update(set(uids))

    def can_get_next(self) -> bool:
        if self.tasks.empty():
            return False

        if self.tasks.queue[0].instruction_type == Instruction.Type.WAIT:
            if len(self.current_running) != 0:
                return False

        return True

    def blocked(self) -> bool:
        if self.tasks.empty():
            return False

        if self.tasks.queue[0].instruction_type == Instruction.Type.WAIT:
            if len(self.current_running) != 0:
                return True

        return False


def parse_instructions(instructions: List[str]) -> List[Instruction]:
    parsed_instructions: List[Instruction] = []

    for instruction in instructions:
        if instruction.startswith("RUN"):
            parsed_instructions.append(Instruction(Instruction.Type.RUN, instruction.split("RUN", 1)[1], uuid4()))
        elif instruction.startswith("WAIT"):
            parsed_instructions.append(Instruction(Instruction.Type.WAIT, "", uuid4()))
        else:
            print(f"Encountered Non Instruction: {instruction}")

    return parsed_instructions
