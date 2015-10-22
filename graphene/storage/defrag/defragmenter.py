

class Defragmenter:
    def __init__(self, base_store, id_store):
        """
        Initialize a Defragmenter instance to use for defragmenting files

        :param base_store: Base store to perform swaps on
        :type base_store: GeneralStore
        :param id_store: Id store for the base store
        :type id_store: IdStore
        :return: Defragmenter instance for defragmenting base files
        :rtype: Defragmenter
        """
        self.baseStore = base_store
        self.idStore = id_store

    def defragment(self):
        """
        Defragments the store and updates corresponding references

        :return: Nothing
        :rtype: None
        """
        # Get total number of blocks (excluding 0)
        total_blocks = self.baseStore.count()
        # Get IDs of empty blocks
        empty_blocks = sorted(self.idStore.get_all_ids())
        # Get IDs of full blocks
        non_empty_blocks = self.non_empty_blocks(empty_blocks, total_blocks)
        # Filter continuous IDs from these full IDs
        full_non_cont_blocks = self.non_continuous_ids(non_empty_blocks)
        # Create table with the needed swaps
        swap_table = self.create_swap_table(full_non_cont_blocks, empty_blocks)
        # Perform the needed swaps
        self.perform_swaps(swap_table)
        # File should not have any remaining ids, clear id store
        self.idStore.clear()
        # Fix the references in any of the files that reference this store and
        # any self-references (if any)
        self.fix_references()

    def perform_swaps(self, swap_table):
        """
        Performs the data swaps specified by the swap table on the given store

        :param swap_table: Dictionary of src->dest index maps for swaps needed
        :type swap_table: dict[int, int]
        :return: Nothing
        :rtype: None
        """
        src_data = self.fetch_data(swap_table.keys())
        for src, dst in swap_table.items():
            self.baseStore.write_to_index_packed_data(dst, src_data[src])

    def fetch_data(self, indexes):
        """
        Fetch data at the given indexes from the store into RAM

        :param indexes: Indexes to fetch the data for
        :type indexes: list[int]
        :return: Dictionary with the index keys and fetched data values
        :rtype: dict[int, str]
        """
        # TODO: split into parts to make this more RAM conservative
        data = {}
        for idx in indexes:
            data[idx] = self.baseStore.read_from_index_packed_data(idx)
        return data

    def fix_references(self):
        """
        Fix any broken references, either within this file or from other files

        :return: Nothing
        :rtype: None
        """
        pass

    @staticmethod
    def non_empty_blocks(empty_ids, total_blocks):
        """
        Return the IDs of full blocks with the given empty IDs and total
        number of blocks

        :param empty_ids: List of empty IDs
        :type empty_ids: list[int]
        :param total_blocks: Total number of blocks
        :type total_blocks: int
        :return: List of full blocks
        :rtype: list[int]
        """
        # Get a list of all the IDs, it's total_blocks - 1 because offsets go
        # up to the total number of blocks - 1
        all_ids = set(range(1, total_blocks - 1))
        return [i for i in all_ids if i not in empty_ids]

    @staticmethod
    def non_continuous_ids(ids):
        """
        Filters out continuous IDs from the list of IDs starting at 1.
        For example:
        Given: [1, 2, 3, 7, 8, 9]
        Filter out continuous: [1, 2, 3]
        Returns: [7, 8, 9]

        :param ids: List of IDs to filter
        :type ids: list[int]
        :return: List of non-continuous IDs
        :rtype: list[int]
        """
        for idx, i in enumerate(sorted(ids)):
            if idx != i:
                return ids[idx:]
        return []

    @staticmethod
    def create_swap_table(full_non_continuous_blocks, empty_blocks):
        """
        Creates a swap table mapping fragmented block IDs to their new
        destination

        :param full_non_continuous_blocks: Sorted list IDs of full
                                           non-continuous blocks
        :type full_non_continuous_blocks: list[int]
        :param empty_blocks: Sorted list of IDs of empty blocks
        :type empty_blocks: list[int]
        :return: Dictionary of src->dest index maps for the swaps needed
        :rtype: dict[int,int]
        """
        num_swaps = len(full_non_continuous_blocks)
        new_slots = list(range(empty_blocks[0], num_swaps))
        return dict(zip(full_non_continuous_blocks, new_slots))
