import pickle
from io import BytesIO, SEEK_CUR


class MessageFrame:

    def __init__(self):
        self.bytes = BytesIO(b'')

    def add_message(self, message):
        pickle.dump(message, file=self.bytes)

    def get_message(self):
        return pickle.load(file=self.bytes)

    def encode(self) -> bytes:
        return self.bytes.getvalue()

    def decode(self, data: bytes):
        self.bytes = BytesIO(data)

    # Not the opposite of empty! check where the cursor in the byte array is
    def available(self) -> bool:
        if self.bytes.read(1) != b'':
            self.bytes.seek(-1, SEEK_CUR)
            return True
        return False

    # check if the frame is empty
    def empty(self):
        return len(self.bytes.getvalue()) == 0
