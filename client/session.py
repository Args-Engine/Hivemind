from common.session_base import SessionBase


class Session(SessionBase):
    def __init__(self):
        super().__init__()
        self.parameters = {}

    def __setitem__(self, key: str, value):
        return self.parameters.__setitem__(key, value)

    def __getitem__(self, item: str):
        return self.parameters.__getitem__(item)

    def __contains__(self, item: str):
        return self.parameters.__contains__(item)