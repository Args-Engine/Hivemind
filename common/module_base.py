import abc
from typing import NoReturn, List, Union

from common.session_base import SessionBase


class ModuleBase(metaclass=abc.ABCMeta):
    def __init__(self, interests: List[Union[str, type]]):
        self.interests = interests

    @abc.abstractmethod
    def handle(self, message_name: str, message_value, session: SessionBase) -> NoReturn:
        pass
