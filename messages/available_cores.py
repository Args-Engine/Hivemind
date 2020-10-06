from typing import Dict


class AvailableCores:
    def __init__(self, available: int, per_workspace: Dict[str, int]):
        self.available = available
        self.per_workspace = per_workspace
