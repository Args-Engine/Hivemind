from collections import deque
from enum import Enum
from queue import Queue
from typing import List, Union, Set
from uuid import uuid4

from client.session import Session


# encapsulate an Instruction
class Instruction:
    class Type(Enum):
        WAIT = 1
        RUN = 2

    def __init__(self, instruction_type: Type, payload: str, unique_identifier):
        self.instruction_type = instruction_type
        self.payload = payload
        self.unique_identifier = unique_identifier


# A Workspace basically consist of many instructions in a fancy Queue
class Workspace:
    def __init__(self, session: Session, tasks: List[Instruction]):
        self.tasks: Queue[Instruction] = Queue()
        self.tasks.queue = deque(tasks)
        self.current_running: Set[str] = set([])
        self.session = session
        self.destroy_on_sight = False

    # Get the next instruction, if no instruction is available, (because the Workspace finished or is waiting)
    # None is returned
    def get_next(self) -> Union[Instruction, None]:

        task = None

        # check if we can get an instruction
        if self.can_get_next():

            # repeat until we have a valid instruction
            while True:

                # check if the tasks became empty in the meantime
                if self.tasks.empty():
                    break

                # get the task
                task = self.tasks.get()

                # check that the instruction is RUN and not WAIT, otherwise keep looping
                if task.instruction_type != Instruction.Type.WAIT:
                    self.current_running.add(task.unique_identifier)
                    break

        return task

    # check in tasks that returned
    def task_returned(self, uids: List[str]):
        self.current_running.difference_update(set(uids))

    # check if tasks are available
    def can_get_next(self) -> bool:
        # check that the queue is not empty
        if self.tasks.empty():
            return False

        # check if the queue is waiting
        if self.tasks.queue[0].instruction_type == Instruction.Type.WAIT:
            if len(self.current_running) != 0:
                return False

        # otherwise all clear
        return True

    def blocked(self) -> bool:
        # check if the queue is blocked (waiting) because of other tasks

        # check if tasks remain
        if self.tasks.empty():
            return False

        # check if the task list is empty
        if self.tasks.queue[0].instruction_type == Instruction.Type.WAIT:
            if len(self.current_running) != 0:
                return True

        return False


def parse_instructions(instructions: List[str]) -> List[Instruction]:
    parsed_instructions: List[Instruction] = []

    # transform lists of strings into lists of instructions
    for instruction in instructions:
        if instruction.startswith("RUN"):
            parsed_instructions.append(Instruction(Instruction.Type.RUN, instruction.split("RUN", 1)[1], uuid4()))
        elif instruction.startswith("WAIT"):
            parsed_instructions.append(Instruction(Instruction.Type.WAIT, "", uuid4()))
        else:
            print(f"Encountered Non Instruction: {instruction}")

    return parsed_instructions
