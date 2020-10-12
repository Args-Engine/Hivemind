from client.modules.dispatcher_module import DispatcherModule
from client.modules.frontend import FrontendModule
from client.net import Client
from client.middleware import Middleware
from common.ping_printer_module import PingPrinterModule

if __name__ == "__main__":

    modules = [PingPrinterModule(),
               DispatcherModule(),
               FrontendModule()]

    middleware = Middleware(modules=modules)

    client = Client(middleware=middleware)

    client.start()

    while middleware.update():
        pass

    client.keep_alive = False