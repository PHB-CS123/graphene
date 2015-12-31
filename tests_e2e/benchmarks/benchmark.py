from collections import OrderedDict

from tests_e2e.setup.e2e_fixture import E2EFixture
from tests_e2e.setup.e2e_utils import E2EUtils
from graphene.utils.timer import CmdTimer


class Benchmark:
    """
    Only used for calculating time it takes to execute a command.
    Does not check for output correctness.
    """
    # Maximum length of the command displayed in characters
    MAX_COMMAND_LENGTH = 30

    def __init__(self, setup_filename, benchmark_filename):
        self.setupFilename = setup_filename
        self.benchmarkFilename = benchmark_filename
        self.e2eUtils = E2EUtils()
        self.e2eFixture = E2EFixture(setup_filename, self.e2eUtils)
        self.timer = CmdTimer()

    def execute(self):
        self.e2eFixture.set_up()
        commands_executed = OrderedDict()
        for command in self.e2eUtils.commands_from_file(self.benchmarkFilename):
            self.timer.start()
            self.e2eUtils.do_command(command)
            self.timer.stop()
            command_key = self.trim_command(command)
            commands_executed[command_key] = self.timer.time_elapsed
        return commands_executed

    def clean_up(self):
        self.e2eFixture.tear_down()

    @classmethod
    def trim_command(cls, command):
        if len(command) < cls.MAX_COMMAND_LENGTH:
            return command
        else:
            return command[:cls.MAX_COMMAND_LENGTH] + "..."
