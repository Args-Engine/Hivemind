from typing import Dict, List


class AvailableCores:
    def __init__(self, available: int, per_workspace: Dict[str, List[str]]):
        self.available = available
        self.per_workspace = per_workspace
