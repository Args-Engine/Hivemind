from common.alive_helper import AliveHelper
from server.middleware import Middleware
from server.modules.scheduler_module import SchedulerModule
from server.modules.storage_module import StorageModule
from server.net import Server

# check client_startup.py for how this work
# the server is basically the same, but with different layers
# technically a module could be compatible for both server and client

if __name__ == "__main__":

    modules = [SchedulerModule(),
               StorageModule(),
               AliveHelper()]

    middleware = Middleware(modules=modules)

    server = Server(middleware=middleware)

    server.start()

    while middleware.update():
        pass

    server.keep_alive = False
