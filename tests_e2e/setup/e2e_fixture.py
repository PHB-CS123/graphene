from graphene.storage.base.graphene_store import GrapheneStore
from tests_e2e.setup.e2e_utils import E2EUtils


class E2EFixture:

    END_OF_COMMAND = ";"

    def __init__(self, setup_file, e2e_utils):
        self.setupFile = open(setup_file, "r")
        self.utils = e2e_utils
        GrapheneStore.TESTING = True
        self.gpStore = GrapheneStore()

    def __del__(self):
        self.tear_down()

    def set_up(self):
        command = ""
        for line in self.setupFile:
            command += self.process_line(line)
            if command.find(self.END_OF_COMMAND) != -1:
                self.utils.do_command(command)
                command = ""

    def tear_down(self):
        self.gpStore.remove_test_datafiles()

    @staticmethod
    def process_line(line):
        """
        Removes newlines from the given line

        :param line: Line to process
        :type line: str
        :return: Processed line
        :rtype: str
        """
        return line.replace("\n", " ")
