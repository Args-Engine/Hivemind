from .execution_done import ExecutionDone
from .execution_request import ExecutionRequest
from .execution_response import ExecutionResponse
from .ping import Ping
from .available_cores import AvailableCores
from .tasks import Tasks
from .workspace_connect import WorkspaceConnect
from .workspace_request import WorkspaceRequest
from .workspace_response import WorkspaceResponse

msg_name_table = {
    Ping: "Ping",
    AvailableCores: "AvailableCores",
    Tasks: "Tasks",
    ExecutionRequest: "ExecutionRequest",
    ExecutionResponse: "ExecutionResponse",
    ExecutionDone: "ExecutionDone",
    WorkspaceRequest: "WorkspaceRequest",
    WorkspaceResponse: "WorkspaceResponse",
    WorkspaceConnect: "WorkspaceConnect"
}


msg_type_table = {v: k for k, v in msg_name_table.items()}
