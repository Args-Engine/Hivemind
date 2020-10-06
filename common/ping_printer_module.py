from typing import NoReturn

from common.module_base import ModuleBase
from common.session_base import SessionBase


class PingPrinterModule(ModuleBase):

    def __init__(self):
        super().__init__()
        self.interests = ["Ping"]

    def handle(self, message_name: str, message_value, session: SessionBase) -> NoReturn:
        if message_name == "Ping":
            print("Received a Ping Pong")
