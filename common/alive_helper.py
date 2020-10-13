import threading
import re
from typing import NoReturn

from common.module_base import ModuleBase
from common.session_base import SessionBase
from common.update_returns import ApplicationExit


# makes sure that an application can quit
# type Y[es] (case insensitive into the console of the application to quit)
class AliveHelper(threading.Thread, ModuleBase):

    # Even though this is a module, it does not actually handle any messages, as such it does
    # also not have any interests
    def handle(self, message_name: str, message_value, session: SessionBase) -> NoReturn:
        pass

    def __init__(self):
        threading.Thread.__init__(self)
        ModuleBase.__init__(self, [])

        self.alive = True
        self.daemon = True
        self.start()

    def run(self):
        # check if input matches the regex, if it does we quit
        while re.match(r"^[Yy](?:es|ES)?$", input('end?>')) is None and self.alive:
            pass
        self.alive = False

    def onUpdate(self):
        # if we are not alive, we respond that the application should quit
        if not self.alive:
            return ApplicationExit()
