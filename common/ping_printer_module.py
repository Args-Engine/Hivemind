from typing import NoReturn

from common.module_base import ModuleBase
from common.session_base import SessionBase


# basically the simplest module you could create
class PingPrinterModule(ModuleBase):

    def __init__(self):
        # inform the overlords that we would like to know
        # whenever a "Ping" message comes along, alternatively we could also literally
        # listen to the Ping object
        # since we do not plan to do anything with the object this method is a bit neater
        super().__init__(["Ping"])

        # alternate method:
        # from messages.ping import Ping
        # super().__init__([Ping])

    def handle(self, message_name: str, message_value, session: SessionBase) -> NoReturn:
        # the middleware will invoke this function whenever a message is received
        # the first parameter is the name of the message, you can check the names
        # of the messages in the dictionary in messages/__init__.py
        # the second one is the actual message just as it is described in the
        # messages module
        # the third one is the Session, this could either be a Client or a Server
        # Session, depending on where your module lives you can expect either-one
        # both of them need to inherit from SessionBase, which is a slightly
        # limited version of each ones Session

        # here we really just care if the message we received is ping. Since this
        # module does not subscribe to any other message this is not necessarily
        # necessary
        if message_name == "Ping":
            # print a lil message to the console that we got a Ping
            print("Received a Ping Pong")
