import os
import shutil

class GrapheneStore:
    TESTING = False

    def __init__(self):
        # Get the project's root directory
        cur_dir = os.getcwd()

        # Directory where database files will be stored
        if GrapheneStore.TESTING:
            self.datafilesDir = cur_dir + "/test_datafiles/"
        else:
            self.datafilesDir = cur_dir + "/datafiles/"

        # Create datafiles directory if it does not exist
        if not os.path.exists(self.datafilesDir):
            os.mkdir(self.datafilesDir)

    def remove_test_datafiles(self):
        if GrapheneStore.TESTING:
            shutil.rmtree(self.datafilesDir)