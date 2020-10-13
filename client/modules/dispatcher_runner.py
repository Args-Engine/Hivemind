import subprocess
import shlex


class Runner:
    def __init__(self, command, workspace,uid):
        self.workspace = workspace
        self.process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd="K:/" + workspace
        )
        self.uid = uid

    def done(self) -> bool:
        p = self.process.poll()
        if p is None:
            return False
        else:
            print(self.process.communicate()[0] + self.process.communicate()[1])
            return True
