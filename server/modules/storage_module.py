import shutil
import string
import time
import xmlrpc.client
from secrets import choice as s_choice
from socket import gethostname
from typing import NoReturn

from common.module_base import ModuleBase
from common.share_helper import CreateElevatedProc, base_path, share_name
from messages import WorkspaceResponse
from messages.workspace_connect import WorkspaceConnect
from server.session import Session

alphabet = string.ascii_letters + string.digits


class StorageModule(ModuleBase):
    hostname = gethostname()

    def __init__(self):
        super().__init__([
            "WorkspaceRequest"
        ])

        # generate user and password for the share
        self.password = ''.join(s_choice(alphabet) for _ in range(128))
        self.user = 'hivemind-user' + ''.join(s_choice(alphabet) for _ in range(2))

        # make sure the share directory exists
        StorageModule._ensure_directory(base_path)

        # create rpc client & boot elevated runner
        self.proxy = xmlrpc.client.ServerProxy('http://localhost:9808')
        self._boot_elevated_runner()

        # create user & share
        print(self.proxy.NetCreateUser(self.user, self.password))
        print(self.proxy.NetShareCreate(self.user))

    def __del__(self):

        # delete user & share
        self.proxy.NetDeleteUser(self.user)
        self.proxy.NetShareDestroy()

        # shutdown the rpc-server
        self._guarded_shutdown()

        # destroy the folder
        shutil.rmtree(base_path)

    def onConnect(self, session: Session):
        # make sure that the client is connected to the storage share
        if 'unc_connected' not in session:
            session.to_send.put(WorkspaceConnect(self.user, self.password, self.hostname))
            session['unc_connected'] = True

    def handle(self, message_name: str, message_value, session: Session) -> NoReturn:
        if message_name == "WorkspaceRequest":
            # the client wants a workspace to work with
            print("Received Workspace Request")
            folder = ''.join(s_choice(alphabet) for i in range(64))
            self._ensure_directory(base_path + '\\' + folder)

            print("Sending WorkspaceResponse")
            session.to_send.put(WorkspaceResponse(workspace=folder))

    @staticmethod
    def _ensure_directory(directory):
        import os
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

    def _boot_elevated_runner(self):

        # try to get admin runner
        try:
            admin = self.proxy.NetCheckAdmin()
            if not admin:
                self._guarded_shutdown()
                self._guarded_create()
                time.sleep(2)

        # if no runner was present boot a new one
        except (xmlrpc.client.Fault,
                xmlrpc.client.ProtocolError,
                ConnectionRefusedError):
            self._guarded_create()

    def _guarded_create(self):

        # create runner
        CreateElevatedProc()

        # wait for it to come online
        ready = False
        while not ready:
            try:
                self.proxy.NetCheckAdmin()
                ready = True
            except (xmlrpc.client.Fault,
                    xmlrpc.client.ProtocolError,
                    ConnectionRefusedError):
                pass

    def _guarded_shutdown(self):

        # send kill command, connection is going to fail afterwards
        # but we don't care
        try:
            self.proxy.exit(0)
        except ConnectionRefusedError:
            pass
