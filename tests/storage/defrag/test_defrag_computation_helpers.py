import unittest
from graphene.storage.defrag.defragmenter import *


class TestDefragmenterComputationHelper(unittest.TestCase):
    def test_full_blocks1(self):
        empty_ids = [1, 2, 3, 8, 9]
        total_blocks = 10
        full_blocks = Defragmenter.full_blocks(empty_ids, total_blocks)
        expected = [4, 5, 6, 7, 10]
        self.assertEqual(full_blocks, expected,
                         "Result full blocks: %s do not equal expected: %s"
                         % (full_blocks, expected))

    def test_full_blocks2(self):
        empty_ids = []
        total_blocks = 10
        full_blocks = Defragmenter.full_blocks(empty_ids, total_blocks)
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(full_blocks, expected,
                         "Result full blocks: %s do not equal expected: %s"
                         % (full_blocks, expected))

    def test_full_blocks3(self):
        empty_ids = [1, 2, 3, 4, 5]
        total_blocks = 5
        full_blocks = Defragmenter.full_blocks(empty_ids, total_blocks)
        expected = []
        self.assertEqual(full_blocks, expected,
                         "Result full blocks: %s do not equal expected: %s"
                         % (full_blocks, expected))

    def test_non_continuous_ids1(self):
        ids = [1, 2, 3, 7, 8, 9]
        continuous = [1, 2, 3]
        non_continuous = [7, 8, 9]
        result = Defragmenter.non_continuous_ids(ids)
        expected = (continuous, non_continuous)
        self.assertEqual(result, expected,
                         "Filtered result: %s does not equal expected: %s"
                         % (result, expected,))

    def test_non_continuous_ids2(self):
        ids = [1, 2, 3, 4, 5, 6]
        continuous = [1, 2, 3, 4, 5, 6]
        non_continuous = []
        result = Defragmenter.non_continuous_ids(ids)
        expected = (continuous, non_continuous)
        self.assertEqual(result, expected,
                         "Filtered result: %s does not equal expected: %s"
                         % (result, expected,))

    def test_non_continuous_ids3(self):
        ids = [2, 3, 4, 5, 6]
        continuous = []
        non_continuous = [2, 3, 4, 5, 6]
        result = Defragmenter.non_continuous_ids(ids)
        expected = (continuous, non_continuous)
        self.assertEqual(result, expected,
                         "Filtered result: %s does not equal expected: %s"
                         % (result, expected,))

    def test_create_swap_table1(self):
        full_non_cont_blks = [12, 13, 15]
        empty_blks = [10, 11, 14]
        expected = {12: 10, 13: 11, 15: 12}
        result = Defragmenter.create_swap_table(full_non_cont_blks, empty_blks)
        self.assertEqual(result, expected,
                         "Resulting swap table: %s does not equal expected: %s"
                         % (result, expected))

    def test_create_swap_table2(self):
        full_non_cont_blks = [12, 13, 15, 16]
        empty_blks = [10, 11, 14]
        expected = {12: 10, 13: 11, 15: 12, 16: 13}
        result = Defragmenter.create_swap_table(full_non_cont_blks, empty_blks)
        self.assertEqual(result, expected,
                         "Resulting swap table: %s does not equal expected: %s"
                         % (result, expected))

    def test_create_swap_table3(self):
        full_non_cont_blks = [12, 14]
        empty_blks = [10, 11, 13]
        expected = {12: 10, 14: 11}
        result = Defragmenter.create_swap_table(full_non_cont_blks, empty_blks)
        self.assertEqual(result, expected,
                         "Resulting swap table: %s does not equal expected: %s"
                         % (result, expected))

    def test_create_swap_table4(self):
        full_non_cont_blks = []
        empty_blks = [10, 11, 13]
        expected = {}
        result = Defragmenter.create_swap_table(full_non_cont_blks, empty_blks)
        self.assertEqual(result, expected,
                         "Resulting swap table: %s does not equal expected: %s"
                         % (result, expected))

    def test_create_swap_table5(self):
        full_non_cont_blks = [12, 14]
        empty_blks = []
        expected = {}
        result = Defragmenter.create_swap_table(full_non_cont_blks, empty_blks)
        self.assertEqual(result, expected,
                         "Resulting swap table: %s does not equal expected: %s"
                         % (result, expected))
