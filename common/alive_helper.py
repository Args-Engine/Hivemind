import threading
import re
from typing import NoReturn

from common.module_base import ModuleBase
from common.session_base import SessionBase
from common.update_returns import ApplicationExit


class AliveHelper(threading.Thread, ModuleBase):

    def handle(self, message_name: str, message_value, session: SessionBase) -> NoReturn:
        pass

    def __init__(self):
        threading.Thread.__init__(self)
        ModuleBase.__init__(self, [])
        self.alive = True
        self.daemon = True
        self.start()

    def run(self):
        while re.match(r"^[Yy](?:es|ES)?$", input('end?>')) is None and self.alive:
            pass
        self.alive = False

    def onUpdate(self):
        if not self.alive:
            return ApplicationExit()
