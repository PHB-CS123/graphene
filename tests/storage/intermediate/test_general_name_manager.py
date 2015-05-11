import unittest
from random import random
from math import ceil

from graphene.storage.intermediate.general_name_manager import *


class TestGeneralNameManagerMethods(unittest.TestCase):
    TEST_FILENAME = "graphenestore.namestore.db"
    TEST_BLOCK_SIZE = 10

    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_init(self):
        """
        Test that initializing a GeneralNameManager succeeds (file is opened)
        """
        try:
            GeneralNameManager(self.TEST_FILENAME, self.TEST_BLOCK_SIZE)
        except IOError:
            self.fail("GeneralNameManager initializer failed: %s"
                      "db file failed to open." % self.TEST_FILENAME)

    def test_double_init(self):
        """
        Test that initializing a GeneralNameManager succeeds when repeated;
        i.e. the old file is reopened and no errors occur.
        """
        try:
            GeneralNameManager(self.TEST_FILENAME, self.TEST_BLOCK_SIZE)
        except IOError:
            self.fail("GeneralNameManager initializer failed: %s"
                      "db file failed to open." % self.TEST_FILENAME)
        try:
            GeneralNameManager(self.TEST_FILENAME, self.TEST_BLOCK_SIZE)
        except IOError:
            self.fail("GeneralNameManager initializer failed on second"
                      "attempt: %s db file failed to open."
                      % self.TEST_FILENAME)

    def test_eof_read(self):
        """
        Test that reading from an empty file returns an EOF
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)
        with self.assertRaises(EOFError):
            name_manager.read_name_at_index(1)

    def test_write_name_1_block(self):
        """
        Tests that writing a name that fits in a single block succeeds
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with the length of the block size
        name = "a" * self.TEST_BLOCK_SIZE
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Read the name back and make sure it is as expected
        self.assertEquals(name, name_manager.read_name_at_index(name_index))

    def test_write_2_names_1_block(self):
        """
        Tests that writing 2 names that fit in a single block succeeds
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with the length of the block size
        name1 = "a" * self.TEST_BLOCK_SIZE
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Create another name with the length of the block size
        name2 = "b" * self.TEST_BLOCK_SIZE
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Read the names back and make sure they are as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))
        self.assertEquals(name2, name_manager.read_name_at_index(name_index2))

    def test_write_name_multiple_blocks(self):
        """
        Tests that writing a name that spans multiple blocks succeeds
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length
        name = "a" * self.random_length()
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Read the name back and make sure it is as expected
        self.assertEquals(name, name_manager.read_name_at_index(name_index))

    def test_mangled_return_none(self):
        """
        Test that when reading a mangled string, the method returns None
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length (longer than one block)
        name = "a" * self.random_length()
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Mangle the name by deleting from the second block (first block intact)
        name_manager.storeManager.delete_item_at_index(name_index + 1)
        # Make sure that the read_name_at_index method returns None
        self.assertEquals(name_manager.read_name_at_index(name_index), None)

    def test_invalid_delete(self):
        """
        Test that deleting a name at a non-starting index throws an error
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length (longer than one block)
        name = "a" * self.random_length()
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Try to mangle the name and expect an index error
        with self.assertRaises(IndexError):
            name_manager.delete_name_at_index(name_index + 1)

    def test_mangled_delete(self):
        """
        Test that when deleting a mangled string, the method returns
        an error (false)
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length (longer than one block)
        name = "a" * self.random_length()
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Mangle the name by deleting from the second block (first block intact)
        name_manager.storeManager.delete_item_at_index(name_index + 1)
        # Make sure that the read_name_at_index method returns None
        self.assertEquals(name_manager.delete_name_at_index(name_index), False)

    def test_write_2_names_multiple_blocks(self):
        """
        Tests that writing 2 names that span multiple blocks succeeds
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length
        name1 = "a" * self.random_length()
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Create another name with a random length
        name2 = "b" * self.random_length()
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Read the names back and make sure they are as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))
        self.assertEquals(name2, name_manager.read_name_at_index(name_index2))

    def test_find_name(self):
        """
        Tests that the starting index of a name can be found correctly
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length
        name1 = "a" * self.random_length()
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Create another name with a random length
        name2 = "b" * self.random_length()
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Create a third name with a random length
        name3 = "c" * self.random_length()
        # Write the name to the name store
        name_index3 = name_manager.write_name(name3)

        # Check that the found starting indexes are as expected
        self.assertEquals(name_index1, name_manager.find_name(name1))
        self.assertEquals(name_index2, name_manager.find_name(name2))
        self.assertEquals(name_index3, name_manager.find_name(name3))

    def test_delete_name_at_index(self):
        """
        Tests that deleting an array at a specific index works
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length
        name1 = "a" * self.random_length()
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Check that the name is as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))

        # Delete the name from the name manager
        name_manager.delete_name_at_index(name_index1)
        # Try to read the name, it should return None
        self.assertEquals(name_manager.read_name_at_index(name_index1), None)

    def test_delete_names_at_index_multiple(self):
        """
        Tests that deleting a name at a specific index works with more than
        one item in the store
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length
        name1 = "a" * self.random_length()
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Check that the name is as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))

        # Create a second name with a random length
        name2 = "b" * self.random_length()
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Check that the name is as expected
        self.assertEquals(name2, name_manager.read_name_at_index(name_index2))

        # Create a third name with a random length
        name3 = "c" * self.random_length()
        # Write the name to the name store
        name_index3 = name_manager.write_name(name3)
        # Check that the name is as expected
        self.assertEquals(name3, name_manager.read_name_at_index(name_index3))

        # Delete the 2nd name from the name store
        name_manager.delete_name_at_index(name_index2)
        # Try to read the name, it should return None
        self.assertEquals(name_manager.read_name_at_index(name_index2), None)
        # Check that the other two are as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))
        self.assertEquals(name3, name_manager.read_name_at_index(name_index3))

        # Delete the 1st name from the name store
        name_manager.delete_name_at_index(name_index1)
        # Try to read the name, it should return None
        self.assertEquals(name_manager.read_name_at_index(name_index1), None)
        # Check that the other two are as expected
        self.assertEquals(name_manager.read_name_at_index(name_index2), None)
        self.assertEquals(name3, name_manager.read_name_at_index(name_index3))

        # Delete the 3rd name from the name store
        name_manager.delete_name_at_index(name_index3)
        # Try to read the name, it should return None
        self.assertEquals(name_manager.read_name_at_index(name_index3), None)
        # Check that the other two are as expected
        self.assertEquals(name_manager.read_name_at_index(name_index2), None)
        self.assertEquals(name_manager.read_name_at_index(name_index1), None)

    @classmethod
    def random_length(cls):
        """
        Generate a random length that spans multiple blocks

        :return: Integer length
        :rtype: int
        """
        # Vary the number of blocks
        randomize1 = ceil(random() * 10) % 10 + 1
        # Vary the number of characters in the last block
        randomize2 = ceil(random() * 10) % 10 + 1
        return int(cls.TEST_BLOCK_SIZE * randomize1 + randomize2)