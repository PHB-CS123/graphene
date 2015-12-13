import os
from struct import Struct

class IndexStore:
    # Size of an index (integer)
    INDEX_SIZE = 4

    def __init__(self, filename):
        # Create the file if it does not exist
        if not os.path.isfile(filename):
            open(filename, "w+").close()
        self.filename = filename
        # Don't read the index set until it's needed
        self.indexSet = None
        # True if there are unsaved changes to the index set
        self.isDirty = False

    def get_index_set(self):
        """
        Load the index set if not already loaded

        :return: Index set loaded from file
        :rtype: set(int)
        """
        if not self.indexSet:
            self.indexSet = self.get_index_set_from_file()
        return self.indexSet

    def handle_insert(self, idx):
        """
        Handle the insertion of the node or relationship into the database

        :param idx: Index of the item
        :type idx: int
        :return: Nothing
        :rtype: None
        """
        self.isDirty = True
        if not self.indexSet:
            self.indexSet = self.get_index_set_from_file()
        self.indexSet.add(idx)

    def handle_delete(self, idx):
        """
        Handle the deletion of a node or relationship from the database

        :param idx: Index of the item
        :type idx: int
        :return: Nothing
        :rtype: None
        """
        self.isDirty = True
        if not self.indexSet:
            self.indexSet = self.get_index_set_from_file()
        self.indexSet.remove(idx)

    def unload_index_set(self):
        """
        Removes the index set from RAM. Flushes it to disk first.

        :return: Nothing
        :rtype: None
        """
        self.write_index_set_to_file()
        self.indexSet = None

    def delete_index(self):
        """
        Deletes the index file

        :return: Nothing
        :rtype: None
        """
        # Clear the index from RAM
        self.indexSet = None
        # Remove the index file
        os.remove(self.filename)

    def get_index_set_from_file(self):
        f = open(self.filename)
        # Get the number of integers in the file to unpack
        f.seek(0, os.SEEK_END)
        idx_amt = f.tell() / self.INDEX_SIZE
        # Get the struct to unpack the integers from the file
        s = self.get_index_struct(idx_amt)
        # Go back to the start of the file
        f.seek(0, os.SEEK_SET)
        # Create index set from unpacked items
        # TODO: more RAM efficient?
        return set(s.unpack(f.read()))

    def write_index_set_to_file(self):
        if not self.indexSet or not self.isDirty:
            return
        f = open(self.filename, "wb")
        # Get the struct to pack the integers to store to the file
        s = self.get_index_struct(len(self.indexSet))
        f.write(s.pack(*self.indexSet))
        # All changes have been flushed
        self.isDirty = False

    @classmethod
    def get_index_struct(cls, index_amt):
        # Structure used for unpacking indexes
        return Struct("= %dI" % index_amt)
