import subprocess
import shlex


class Runner:
    def __init__(self, command, workspace):
        self.workspace = workspace
        self.process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=workspace
        )

    def done(self) -> bool:
        p = self.process.poll()
        if p is None:
            return False
        else:
            return True
