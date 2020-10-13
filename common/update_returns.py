# things you can return from onUpdate to do different things

class ApplicationExit:
    pass


class EmitError:
    def __init__(self, error):
        self.error = error
