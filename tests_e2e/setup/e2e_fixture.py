from graphene.storage.base.graphene_store import GrapheneStore


class E2EFixture:
    """
    :type utils: E2EUtils
    """

    END_OF_COMMAND = ";"

    def __init__(self, setup_file, e2e_utils):
        self.setupFilename = setup_file
        self.utils = e2e_utils
        GrapheneStore.TESTING = True
        self.gpStore = GrapheneStore()

    def __del__(self):
        self.tear_down()

    def set_up(self):
        for command in self.utils.commands_from_file(self.setupFilename):
            self.utils.do_command(command)

    def tear_down(self):
        self.gpStore.remove_test_datafiles()
