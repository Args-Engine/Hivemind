import subprocess
import shlex


class Runner:
    def __init__(self, command, workspace, uid):

        self.workspace = workspace
        self.uid = uid

        # set up tasks
        self.process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd="K:/" + workspace
        )

    def done(self) -> bool:
        p = self.process.poll()

        # when p is None the task finished
        if p is None:
            return False
        else:
            # also get the output of the task (this could be put into a different thread to print directly, but it is
            # a lot of work just to get that working in real time)
            print(self.process.communicate()[0] + self.process.communicate()[1])
            return True
