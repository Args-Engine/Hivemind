from client.modules.dispatcher_module import DispatcherModule
from client.modules.frontend import FrontendModule
from client.modules.share_connector import ShareConnector
from client.modules.workspace_setup import WorkspaceSetup
from client.net import Client
from client.middleware import Middleware
from common.ping_printer_module import PingPrinterModule


if __name__ == "__main__":
    # modules to install into the client
    # this makes it so that we could technically have a client
    # without a frontend
    modules = [PingPrinterModule(),
               DispatcherModule(),
               FrontendModule(),
               ShareConnector(),
               WorkspaceSetup()]

    # no frontend and no way to query tasks, basic runner
    """
    
    modules = [ DipatcherModule(),
                ShareConnector()]
    
    """

    # no frontend headless (there does not exists a module to query tasks without a frontend yet, but it could be done
    # pretty easily
    """
    
    modules = [ ImaginaryNonFrontendQueryModule(),
                DispatcherModule(),
                ShareConnector(),
                WorkspaceSetup()]
    
    """

    # no execution just task emplacement
    """
    
    modules = [ FrontendModule(),
                WorkspaceSetup()]
        
    
    """

    # create client middleware with all the modules
    middleware = Middleware(modules=modules)

    # create client network layer with middleware
    client = Client(middleware=middleware)

    # boot network layer
    client.start()

    # keep updating the middleware
    while middleware.update():
        pass

    # kill the client after the middleware is done
    client.keep_alive = False