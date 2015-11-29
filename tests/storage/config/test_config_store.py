import unittest

from graphene.storage.config.config_store import ConfigStore
from graphene.storage.base.graphene_store import GrapheneStore


class TestArrayStoreMethods(unittest.TestCase):
    def setUp(self):
        """
        Set up the GrapheneStore so that it writes datafiles to the testing
        directory
        """
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_empty_init(self):
        """
        Test that initializing an empty ConfigStore succeeds
        (file is opened successfully)
        """
        try:
            ConfigStore()
        except IOError:
            self.fail("ConfigStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty ConfigStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            ConfigStore()
        except IOError:
            self.fail("ConfigStore initializer failed: "
                      "db file failed to open.")
        try:
            ConfigStore()
        except IOError:
            self.fail("ConfigStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_set_config_no_section_bool(self):
        """
        Test that a config is set properly and stored when store is closed.
        Write config to default section. Value is a bool.
        """
        name = "Testing"
        e_val = True
        config = ConfigStore()
        config.set_config(name, e_val)
        del config
        reopen_config = ConfigStore()
        a_val = reopen_config.get_config(name, ConfigStore.ConfigType.bool)
        msg = "Actual val: %s does not equal expected val: %s for name: %s"
        self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_set_config_no_section_int(self):
        """
        Test that a config is set properly and stored when store is closed.
        Write config to default section. Value is an int.
        """
        name = "Favorite Number"
        e_val = 42
        config = ConfigStore()
        config.set_config(name, e_val)
        del config
        reopened_config = ConfigStore()
        a_val = reopened_config.get_config(name, ConfigStore.ConfigType.int)
        msg = "Actual val: %s does not equal expected val: %s for name: %s"
        self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_set_config_no_section_str(self):
        """
        Test that a config is set properly and stored when store is closed.
        Write config to default section. Value is a string.
        """
        name = "DB Name"
        e_val = "Graphene"
        config = ConfigStore()
        config.set_config(name, e_val)
        del config
        reopened_config = ConfigStore()
        a_val = reopened_config.get_config(name, ConfigStore.ConfigType.string)
        msg = "Actual val: %s does not equal expected val: %s for name: %s"
        self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_set_config_section_bool(self):
        """
        Test that a config is set properly and stored when store is closed.
        Write config to custom section. Value is a bool.
        """
        name = "Testing"
        e_val = True
        sec = "Favorite Section"
        config = ConfigStore()
        config.set_config(name, e_val, sec)
        del config
        reopen_config = ConfigStore()
        a_val = reopen_config.get_config(name, ConfigStore.ConfigType.bool, sec)
        msg = "Actual val: %s does not equal expected val: %s for name: %s"
        self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_set_config_section_int(self):
        """
        Test that a config is set properly and stored when store is closed.
        Write config to custom section. Value is an int.
        """
        name = "Favorite Number"
        e_val = 42
        sec = "Favorite Section"
        config = ConfigStore()
        config.set_config(name, e_val, sec)
        del config
        reopened_config = ConfigStore()
        a_val = reopened_config.get_config(name, ConfigStore.ConfigType.int, sec)
        msg = "Actual val: %s does not equal expected val: %s for name: %s"
        self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_set_config_section_str(self):
        """
        Test that a config is set properly and stored when store is closed.
        Write config to custom section. Value is a string.
        """
        name = "DB Name"
        e_val = "Graphene"
        sec = "Favorite Section"
        config = ConfigStore()
        config.set_config(name, e_val, sec)
        del config
        reopened_config = ConfigStore()
        a_val = reopened_config.get_config(name, ConfigStore.ConfigType.string, sec)
        msg = "Actual val: %s does not equal expected val: %s for name: %s"
        self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_set_config_multiple_values(self):
        """
        Test several configs are set properly and stored when store is closed.
        """
        name1 = "name 1"
        val1 = 1
        name2 = "name 2"
        val2 = False
        name3 = "name 3"
        val3 = "hi"
        name4 = "name 4"
        val4 = 4
        names = [name1, name2, name3, name4]
        values = [val1, val2, val3, val4]
        types = [ConfigStore.ConfigType.int, ConfigStore.ConfigType.bool,
                 ConfigStore.ConfigType.string, ConfigStore.ConfigType.int]

        config = ConfigStore()
        for i, j in zip(names, values):
            config.set_config(i, j)
        del config

        reopened_config = ConfigStore()
        for i, name in enumerate(names):
            a_val = reopened_config.get_config(name, types[i])
            e_val = values[i]
            msg = "Actual val: %s does not equal expected val: %s for name: %s"
            self.assertEqual(a_val, e_val, msg % (a_val, e_val, name))

    def test_get_config_fails_for_undefined_type(self):
        """
        Test that getting a config of a certain type fails for an undefined type
        """
        name = "DB Name"
        e_val = "Graphene"
        config = ConfigStore()
        config.set_config(name, e_val)
        del config
        reopened_config = ConfigStore()
        with self.assertRaises(TypeError):
            reopened_config.get_config(name, ConfigStore.ConfigType.undefined)

    def test_get_config_returns_none_for_missing_name_empty_config(self):
        """
        Test that getting a config for a missing name returns None. Empty config
        file.
        """
        config = ConfigStore()
        val = config.get_config("missing", ConfigStore.ConfigType.undefined)
        self.assertIsNone(val)

    def test_get_config_returns_none_for_missing_name(self):
        """
        Test that getting a config for a missing name returns None. Non-empty
        config file.
        """
        name = "DB Name"
        e_val = "Graphene"
        config = ConfigStore()
        config.set_config(name, e_val)
        del config
        r_config = ConfigStore()
        val = r_config.get_config("missing", ConfigStore.ConfigType.undefined)
        self.assertIsNone(val)
