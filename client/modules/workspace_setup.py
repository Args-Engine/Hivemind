from typing import NoReturn

from common.module_base import ModuleBase
from common.session_base import SessionBase
from common.update_returns import EmitError


class WorkspaceSetup(ModuleBase):

    def __init__(self):
        super().__init__(["WorkspaceResponse"])

    def handle(self, message_name: str, message_value, session: SessionBase) -> NoReturn:
        if 'workspace-base-path' in session:
            pass
        else:
            return EmitError("Error, received workspace response without active workspace location")
