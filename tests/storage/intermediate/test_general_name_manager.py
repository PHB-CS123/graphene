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
        result = name_manager.read_name_at_index(1)
        self.assertEquals(result, EOF)

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
        Test that when reading a mangled string, the method returns None.
        Assuming the mangling is not at the end of the file
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length (longer than one block)
        name = "a" * (2 * self.TEST_BLOCK_SIZE + 1)
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Mangle the name by deleting from the second block (first block intact)
        name_manager.storeManager.delete_item_at_index(name_index + 1)
        # Make sure that the read_name_at_index method returns None
        self.assertEquals(name_manager.read_name_at_index(name_index), None)

    def test_mangled_return_EOF(self):
        """
        Test that when reading a mangled string, the method returns None or EOF.
        Assuming the mangling is at the end of the file (the file is truncated)
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)

        # Create a name with a random length (longer than one block)
        name = "a" * (2 * self.TEST_BLOCK_SIZE)
        # Write the name to the name store
        name_index = name_manager.write_name(name)
        # Mangle the name by deleting from the second block (first block intact)
        name_manager.storeManager.delete_item_at_index(name_index + 1)
        # Make sure that the read_name_at_index method returns EOF
        self.assertEquals(name_manager.read_name_at_index(name_index), EOF)

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

    def test_find_names(self):
        """
        Tests that the starting index of various names can be found correctly
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
        # Create a fourth name with a random length
        name4 = "d" * self.random_length()
        # Write the name to the name store
        name_index4 = name_manager.write_name(name4)

        # Check that none is returned for empty array
        no_names = name_manager.find_names([])
        self.assertIsNone(no_names)
        # Check that the found starting indexes are as expected
        name_indexes23 = name_manager.find_names([name2, name3])
        self.assertEquals([name_index2, name_index3], name_indexes23)
        # Check that the found starting indexes are as expected when in
        # non-increasing order
        name_indexes213 = name_manager.find_names([name2, name1, name3])
        self.assertEquals([name_index2, name_index1, name_index3],
                          name_indexes213)

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
        # Try to read the name, it should return None or EOF
        result = name_manager.read_name_at_index(name_index1)
        self.assertTrue(result is None or result is EOF)

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
        # Try to read the name, it should return None or EOF
        name2_file = name_manager.read_name_at_index(name_index2)
        self.assertTrue(name2_file is None or name2_file is EOF)
        # Check that the other two are as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))
        self.assertEquals(name3, name_manager.read_name_at_index(name_index3))

        # Delete the 1st name from the name store
        name_manager.delete_name_at_index(name_index1)
        # Try to read the name, it should return None
        name1_file = name_manager.read_name_at_index(name_index1)
        self.assertTrue(name1_file is None or name1_file is EOF)
        # Check that the other two are as expected
        name2_file = name_manager.read_name_at_index(name_index2)
        self.assertTrue(name2_file is None or name2_file is EOF)
        self.assertEquals(name3, name_manager.read_name_at_index(name_index3))

        # Delete the 3rd name from the name store
        name_manager.delete_name_at_index(name_index3)
        # Try to read the name, it should return None
        name3_file = name_manager.read_name_at_index(name_index3)
        self.assertTrue(name3_file is None or name3_file is EOF)
        # Check that the other two are as expected
        name1_file = name_manager.read_name_at_index(name_index1)
        self.assertTrue(name1_file is None or name1_file is EOF)
        name2_file = name_manager.read_name_at_index(name_index2)
        self.assertTrue(name2_file is None or name2_file is EOF)

    def test_update_name_at_index_same_size(self):
        """
        Test that updating a name at a certain starting index works with
        same size updates
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)
        # Create a name that spans a single block
        name1 = "a" * self.TEST_BLOCK_SIZE
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Check that the name is as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))

        # Update the name spanning a single block
        name1_u = "b" * (self.TEST_BLOCK_SIZE - 1)
        name_manager.update_name_at_index(name_index1, name1_u)
        self.assertEquals(name1_u, name_manager.read_name_at_index(name_index1))

        # Create a name that spans two blocks
        name2 = "b" * (2 * self.TEST_BLOCK_SIZE)
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Check that the name is as expected
        self.assertEquals(name2, name_manager.read_name_at_index(name_index2))

        # Update it with a name spanning two blocks
        name2_u = "c" * (2 * self.TEST_BLOCK_SIZE - 1)
        name_manager.update_name_at_index(name_index2, name2_u)
        self.assertEquals(name2_u, name_manager.read_name_at_index(name_index2))

    def test_update_name_at_index_smaller_size(self):
        """
        Test that updating a name at a certain starting index works, with
        shorter-sized updates. Check that it deletes old items.
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)
        # Create a name that spans a three blocks
        name1 = "d" * (3 * self.TEST_BLOCK_SIZE)
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Check that the name is as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))

        # Update it with a name spanning a single block
        name1_u = "c" * (self.TEST_BLOCK_SIZE - 1)
        name_manager.update_name_at_index(name_index1, name1_u)
        self.assertEquals(name1_u, name_manager.read_name_at_index(name_index1))
        # Make sure the residue spots are deleted
        old_spot1 = name_manager.storeManager.get_item_at_index(name_index1 + 1)
        self.assertTrue(old_spot1 is None or old_spot1 is EOF)
        old_spot2 = name_manager.storeManager.get_item_at_index(name_index1 + 2)
        self.assertTrue(old_spot2 is None or old_spot2 is EOF)

        # Create a name that spans 4 blocks
        name2 = "e" * (4 * self.TEST_BLOCK_SIZE)
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Check that the name is as expected
        self.assertEquals(name2, name_manager.read_name_at_index(name_index2))

        # Update it with a name spanning no blocks
        name2_u = "" 
        name_manager.update_name_at_index(name_index2, name2_u)
        self.assertEquals(name2_u, name_manager.read_name_at_index(name_index2))
        # Make sure the residue spots are deleted
        old_spot3 = name_manager.storeManager.get_item_at_index(name_index2 + 3)
        self.assertTrue(old_spot3 is None or old_spot3 is EOF)

    def test_update_name_at_index_longer_size(self):
        """
        Test that updating a name at a certain starting index works, with
        longer sized updates.
        """
        name_manager = GeneralNameManager(self.TEST_FILENAME,
                                          self.TEST_BLOCK_SIZE)
        # Create a name that spans a three blocks
        name1 = "g" * (3 * self.TEST_BLOCK_SIZE)
        # Write the name to the name store
        name_index1 = name_manager.write_name(name1)
        # Check that the name is as expected
        self.assertEquals(name1, name_manager.read_name_at_index(name_index1))

        # Update it with a name spanning 4 blocks
        name1_u = "h" * (4 * self.TEST_BLOCK_SIZE)
        name_manager.update_name_at_index(name_index1, name1_u)
        self.assertEquals(name1_u, name_manager.read_name_at_index(name_index1))

        # Create a name that spans 1 block
        name2 = "i" * self.TEST_BLOCK_SIZE
        # Write the name to the name store
        name_index2 = name_manager.write_name(name2)
        # Check that the name is as expected
        self.assertEquals(name2, name_manager.read_name_at_index(name_index2))

        # Update it with a name spanning 6 blocks
        name2_u = "j" * (6 * self.TEST_BLOCK_SIZE)
        name_manager.update_name_at_index(name_index2, name2_u)
        self.assertEquals(name2_u, name_manager.read_name_at_index(name_index2))

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