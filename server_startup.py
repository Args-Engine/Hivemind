from common.alive_helper import AliveHelper
from common.ping_printer_module import PingPrinterModule
from server.modules.scheduler_module import SchedulerModule
from server.modules.storage_module import StorageModule
from server.net import Server
from server.middleware import Middleware

if __name__ == "__main__":

    modules = [PingPrinterModule(),
               SchedulerModule(),
               StorageModule()]

    middleware = Middleware(modules=modules)

    server = Server(middleware=middleware)

    server.start()

    h = AliveHelper()

    while h.alive:
        middleware.update()

    server.keep_alive = False