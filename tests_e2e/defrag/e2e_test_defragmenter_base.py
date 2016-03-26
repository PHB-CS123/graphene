from tests_e2e.setup.e2e_fixture import E2EFixture
from tests_e2e.setup.e2e_utils import E2EUtils

from graphene.storage.defrag_manager import DefragManager


class E2ETestDefragmenterBase(object):

    def __init__(self, setup_filename, query_cmds_filename, delete_cmds_filename):
        super(E2ETestDefragmenterBase, self).__init__()
        self.setupFilename = setup_filename
        self.queryCmdsFilename = query_cmds_filename
        self.deleteCmdsFilename = delete_cmds_filename
        self.e2eUtils = E2EUtils()
        self.e2eFixture = E2EFixture(setup_filename, self.e2eUtils)

    def execute_with_no_defrag(self, print_log=True):
        self.e2eFixture.set_up()
        if print_log:
            print("Running and re-running commands to compare output...")
        for command in self.e2eUtils.commands_from_file(self.queryCmdsFilename):
            self.e2eUtils.do_command(command)
            success = self.e2eUtils.re_run_previous_command()
            if not success:
                f_msg = "Running command %s failed for no defrag control case."\
                        "Output differs between subsequent executions."
                if print_log:
                    print(f_msg % command)
                return success
        return False

    def execute_with_defrag(self, print_log=True):
        if print_log: print("Setting up...")
        self.e2eFixture.set_up()
        output = []

        if print_log: print("Running deletion commands...")
        # Run the delete commands to fragment the database a bit
        for cmd in self.e2eUtils.commands_from_file(self.deleteCmdsFilename):
            self.e2eUtils.do_command(cmd)

        if print_log: print("Capturing query output before defragmentation...")
        query_commands = self.e2eUtils.commands_from_file(self.queryCmdsFilename)
        # Save query outputs before fragmentation
        for cmd in query_commands:
            self.e2eUtils.do_command(cmd)
            output.append(self.e2eUtils.previousOutputIO)

        if print_log: print("Defragmenting the database...")
        # Now defragment the database
        # TODO: fix full defrag
        # DefragManager(self.e2eUtils.testServer.storage_manager).full_defragment()
        sm = self.e2eUtils.testServer.storage_manager
        DefragManager(sm).defragment(sm.node_manager)

        if print_log: print("Comparing output after defragmentation...")
        # Run the commands again and compare the output
        for i, cmd in enumerate(query_commands):
            success = self.e2eUtils.do_command_cmp(cmd, output[i].getvalue())
            if not success:
                f_msg = "Running command %s failed after defragmentation."\
                        "Output differs between subsequent executions."
                if print_log:
                    print(f_msg % cmd)
                return success
        return False
