from client.modules.dispatcher_module import DispatcherModule
from client.net import Client
from client.middleware import Middleware
from common.alive_helper import AliveHelper
from common.ping_printer_module import PingPrinterModule

if __name__ == "__main__":

    modules = [PingPrinterModule(),
               DispatcherModule()]

    middleware = Middleware(modules=modules)

    client = Client(middleware=middleware)

    client.start()

    h = AliveHelper()

    while h.alive:
        middleware.update()
