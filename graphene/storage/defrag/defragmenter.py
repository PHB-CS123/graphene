from struct import Struct

from graphene.storage.base.property_store import PropertyStore, Property
from reference_map import TypeReferenceMap, kArrayType, kStringType, kProperty,\
                          kPropertyTypeOffset, kPropertyPayloadOffset, \
                          kArrayPayloadOffset


class Defragmenter:
    # Format string for a reference type struct (integer)
    REF_STRUCT_FORMAT_STR = "= I"
    # Variable size format string for a reference type struct
    VAR_SIZE_REF_STRUCT_FORMAT_STR = "= %dI"
    # Format string for a type enum value (char)
    TYPE_STRUCT_FORMAT_STR = "= B"

    def __init__(self, base_store, id_store, referencing_stores, is_name=False):
        """
        Initialize a Defragmenter instance to use for defragmenting files

        :param base_store: Base store to perform swaps on
        :type base_store: GeneralStore
        :param id_store: Id store for the base store
        :type id_store: IdStore
        :param referencing_stores: Stores that reference this store
        :type referencing_stores: list[GeneralStore]
        :param is_name: Whether the given store to defragment is a name store
        :type is_name: bool
        :return: Defragmenter instance for defragmenting base files
        :rtype: Defragmenter
        """
        # Store to defragment
        self.baseStore = base_store
        # ID store that corresponds to this base store
        self.idStore = id_store
        # Reference map for the current store
        self.referenceMap = TypeReferenceMap[base_store.STORAGE_TYPE.__name__]
        # Base stores that reference this store
        self.referencingStores = referencing_stores
        # Structure for a reference type (int, 4 bytes)
        self.referenceStruct = Struct(self.REF_STRUCT_FORMAT_STR)
        # Structure for a type enum (char, 1 byte)
        self.typeStruct = Struct(self.TYPE_STRUCT_FORMAT_STR)
        # Whether we are defragmenting a name store
        # Edge Case: We have to handle names separately from strings since
        # they are kept in separate db files.
        self.isName = is_name
        # Whether self references should be updated for this file
        self.shouldUpdateSelfRef = \
            self.baseStore.STORAGE_TYPE.__name__ in self.referenceMap

    def defragment(self):
        """
        Defragments the store and updates corresponding references

        :return: Nothing
        :rtype: None
        """
        # Get IDs of empty blocks
        empty_blocks = sorted(self.idStore.get_all_ids())
        # We're done if there are no empty blocks to defragment
        if len(empty_blocks) == 0: return
        # Get total number of blocks (excluding 0)
        total_num_blocks = self.baseStore.count()
        # Get IDs of full blocks
        full_blocks = self.full_blocks(empty_blocks, total_num_blocks)
        # Split into continuous IDs and non-continuous ids from full IDs
        full_cont_blocks, full_non_cont_blocks = \
            self.non_continuous_ids(full_blocks)
        # Create table with the needed swaps
        swap_table = self.create_swap_table(full_non_cont_blocks, empty_blocks)

        # Perform the needed swaps
        self.perform_swaps(swap_table)
        # Trim the end of the defragmented file, full blocks have been shifted
        self.baseStore.truncate_file(len(empty_blocks))
        # File should not have any remaining ids, clear id store
        self.idStore.clear()
        # Fix self references in this store (if any)
        if self.shouldUpdateSelfRef:
            # Remaining self-reference offsets that need to be updated
            self.fix_references(swap_table, self.baseStore,
                                self.referenceMap, full_cont_blocks)
        # Fix the references in any of the files that reference this store
        self.fix_external_references(swap_table)

    def perform_swaps(self, swap_table):
        """
        Performs the data swaps specified by the swap table on the given store

        :param swap_table: Dictionary of src->dest index maps for swaps needed
        :type swap_table: dict[int, int]
        :return: Nothing
        :rtype: None
        """
        src_data = self.fetch_data(swap_table)
        for src, dst in swap_table.items():
            self.baseStore.write_to_index_packed_data(dst, src_data[src])

    def fetch_data(self, swap_table):
        """
        Fetch data at the given indexes from the store into RAM

        :param swap_table: Dictionary of src->dest index maps for swaps needed
        :type swap_table: dict[int, int]
        :return: Dictionary with the index keys and fetched data values
        :rtype: dict[int, str]
        """
        ref_map = self.referenceMap
        # TODO: split into parts to make this more RAM conservative
        data = {}
        for idx in swap_table.keys():
            packed_data = self.baseStore.read_from_index_packed_data(idx)
            if self.shouldUpdateSelfRef:
                store_type = self.baseStore.STORAGE_TYPE.__name__
                packed_data = self.update_references(ref_map, packed_data,
                                                     swap_table, store_type)
            data[idx] = packed_data
        return data

    def update_references(self, ref_map, packed_data, swap_table, store_type):
        """
        Updates the packed data if any references within have changed

        :param ref_map: Map of references for this packed data
        :type ref_map: dict[str, list[int]]
        :param packed_data: Packed data to update
        :type packed_data: str
        :param swap_table: Dictionary of src->dest index maps for updates needed
        :type swap_table: dict[int, int]
        :param store_type: STORAGE_TYPE.__name__ of the packed data's store
        :type store_type: str
        :return: Updated packed data
        :rtype: str
        """
        # Type currently being defragmented
        defrag_type = self.baseStore.STORAGE_TYPE.__name__
        # Size of the reference struct (4 bytes)
        ref_size = self.referenceStruct.size
        # Whether we are defragmenting a string type, but not a name
        is_string_but_not_name = self.is_string_but_not_name()
        # Edge Case: defragmenting a string type, but not a name type and
        # updating a property store. Property may contain a string reference.
        # If this is the case, there is nothing else to update since name
        # references are not updated when defragmenting strings.
        if is_string_but_not_name and store_type == kProperty:
            return self.handle_prop_payload_reference(swap_table, packed_data)
        # Edge Case: defragmenting a string type, but not a name type and
        # updating an array store. Array may be a string array containing
        # string references.
        # If this is the case, there is nothing else to update since name
        # references are not updated when defragmenting strings.
        elif is_string_but_not_name and store_type == kArrayType:
            return self.handle_string_array_references(swap_table, packed_data)
        # We need a reference map for all other cases
        assert defrag_type in ref_map, \
            "Can't update defrag references if reference map has none"
        # New packed data after updates
        new_packed_data = ""
        prev_ending = 0
        for offset in ref_map[defrag_type]:
            offset_val = self.value_at_offset(packed_data, offset)
            # If the value at the current offset is a reference that needs
            # to be updated, do so.
            if offset_val in swap_table:
                new_packed_data += packed_data[prev_ending:offset] + \
                    self.referenceStruct.pack(swap_table[offset_val])
            else:
                new_packed_data += packed_data[prev_ending:offset + ref_size]
            prev_ending = offset + ref_size
        # Append any remaining packed data
        new_packed_data += packed_data[prev_ending:]
        return new_packed_data

    def fix_references(self, swap_table, base_store, ref_map, id_fix_range):
        """
        Fixes references for the given file offsets that may have changed.

        :param swap_table: Dictionary of src->dest index maps for swaps done
        :type swap_table: dict[int, int]
        :param base_store: Store that needs references fixed
        :type base_store: GeneralStore
        :param ref_map: Reference map with the offsets for reference updates
        :type ref_map: dict[str, list[int]]
        :param id_fix_range: Range of IDs that might need their references fixed
        :type id_fix_range: collections.Iterable[int]
        :return: Nothing
        :rtype: None
        """
        # Type store whose references are being fixed
        store_type = base_store.STORAGE_TYPE.__name__
        # Edge Case: We need a reference map when updating references in any
        # store type except when defragmenting a string store and updating
        # string array payload references (all refs. to update are in payload)
        assert ref_map is not None or \
            (self.is_string_but_not_name() and store_type == kArrayType), \
            "Need reference map offsets to fix refs."
        # Edge Case: Array type is being defragmented and we are updating a
        # property store. In this case the Property payload may or may not
        # contain a reference to an Array. Reference map is unused.
        if self.baseStore.STORAGE_TYPE.__name__ == kArrayType and \
                isinstance(base_store, PropertyStore):
            # Update the property payloads for the array type
            self.handle_prop_payload_references(swap_table, base_store,
                                                id_fix_range)
            return

        for block_id in id_fix_range:
            # Update references
            packed_data = base_store.read_from_index_packed_data(block_id)
            new_packed_data = self.update_references(ref_map, packed_data,
                                                     swap_table, store_type)
            # Only re-write the data if it has changed
            if packed_data != new_packed_data:
                base_store.write_to_index_packed_data(block_id, new_packed_data)

    def fix_external_references(self, swap_table):
        """
        Fix changed references in any files that reference this file

        :param swap_table: Dictionary of src->dest index maps for swaps done
        :type swap_table: dict[int, int]
        :return: Nothing
        :rtype: None
        """
        for store in self.referencingStores:
            ref_map = TypeReferenceMap[store.STORAGE_TYPE.__name__]
            id_fix_range = xrange(1, store.count() + 1)
            self.fix_references(swap_table, store, ref_map, id_fix_range)

    def type_value_at_offset(self, packed_data, offset):
        """
        Returns the char value for the type of the packed data at the offset

        :param packed_data: Packed data to get type from
        :type packed_data: str
        :param offset: Offset to look for value
        :type offset: int
        :return: Enum value at the given offset in the packed data
        :rtype: int
        """
        packed_value = packed_data[offset:offset+self.typeStruct.size]
        return self.typeStruct.unpack(packed_value)[0]

    def value_at_offset(self, packed_data, offset):
        """
        Returns the integer value in the packed data at the given offset

        :param packed_data: Packed data to get value from
        :type packed_data: str
        :param offset: Offset to look for value
        :type offset: int
        :return: Integer value at the given offset in the packed data
        :rtype: int
        """
        packed_value = packed_data[offset:offset+self.referenceStruct.size]
        return self.referenceStruct.unpack(packed_value)[0]

    # ---------------------- Edge Cases ---------------------- #
    def handle_prop_payload_references(self, swap_table, base_store,
                                       id_fix_range):
        """
        Handle when the property payload is a reference type, i.e. string or
        array reference.

        :param swap_table: Swap table to check for reference in
        :type swap_table: dict[int, int]
        :param base_store: Base store to update references of
        :type base_store: GeneralStore
        :param id_fix_range: Range of IDs that might need their references fixed
        :type id_fix_range: collections.Iterable[int]
        :return: Nothing
        :rtype: None
        """
        for block_idx in id_fix_range:
            # Update references if property type is a reference type
            packed_data = base_store.read_from_index_packed_data(block_idx)
            new_packed_data = \
                self.handle_prop_payload_reference(swap_table, packed_data)
            # Only rewrite the packed data to store if references were changed
            if packed_data != new_packed_data:
                base_store.write_to_index_packed_data(block_idx,
                                                      new_packed_data)

    def handle_prop_payload_reference(self, swap_table, packed_data):
        """
        Modifies the property packed data payload if it is a reference type
        to an array or string type that is in the swap table.

        :param swap_table: Swap table to check for reference in
        :type swap_table: dict[int, int]
        :param packed_data: Property packed data to modify if it contains a
                            reference in the swap table
        :type packed_data: str
        :return: Modified packed data, or original if not reference type or if
                 the reference is not in the swap table
        :rtype: str
        """
        # TODO: swap these checks to the most unlikely one being first
        old_ref = self.value_at_offset(packed_data, kPropertyPayloadOffset)
        # Don't update if a swap didn't happen for the payload reference
        if old_ref not in swap_table:
            return packed_data
        # Property payload is not a reference type being defragmented
        if not self.property_type_is_defrag_reference(packed_data):
            return packed_data
        # Swap the payload reference with the new reference
        return packed_data[:kPropertyPayloadOffset] + \
            self.referenceStruct.pack(swap_table[old_ref])

    def handle_string_array_references(self, swap_table, packed_data):
        """
        Update references in the payload of the given array packed data

        :param swap_table: Swap table to get references to change from
        :type swap_table: dict[int, int]
        :param packed_data: Property packed data to modify if it contains a
                            reference in the swap table
        :type packed_data: str
        :return: Packed data with any references updated
        :rtype: str
        """
        header = packed_data[:kArrayPayloadOffset]
        payload = packed_data[kArrayPayloadOffset:]
        return header + self.update_string_array_references(swap_table, payload)

    def update_string_array_references(self, swap_table, payload):
        """
        Update string array references in the given payload to reflect the new
        swapped offsets

        :param swap_table: Swap table to get references to change from
        :type swap_table: dict[int, int]
        :param payload: Packed payload string array containing string offsets
        :type payload: str
        :return: Updated, packed payload reflecting new offsets
        :rtype: str
        """
        # If this is a string array, then every value in the array must be a
        # reference type (int)
        num_items = len(payload) / self.referenceStruct.size
        ref_struct = Struct(self.VAR_SIZE_REF_STRUCT_FORMAT_STR % num_items)
        # Update any swapped references
        old = ref_struct.unpack(payload)
        new = map(lambda x: x if x not in swap_table else swap_table[x], old)
        return ref_struct.pack(*new)

    def property_type_is_defrag_reference(self, packed_data):
        """
        Returns whether the property type of the packed data is a reference
        to the type that is currently being defragmented.

        :param packed_data: Packed data to perform check on
        :type packed_data: str
        :return: True if the ref. type is the type currently being defragmented
        :rtype: bool
        """
        type_value = self.type_value_at_offset(packed_data, kPropertyTypeOffset)
        property_type = Property.PropertyType(type_value)
        if Property.type_is_array(property_type):
            return self.baseStore.STORAGE_TYPE.__name__ == kArrayType
        elif Property.type_is_string(property_type):
            return self.baseStore.STORAGE_TYPE.__name__ == kStringType
        else:
            return False

    def is_string_but_not_name(self):
        """
        Whether we are defragmenting a string type, but not a name string type.

        :return: True if we are defragmenting a string type that is not a name
        :rtype: bool
        """
        defrag_type = self.baseStore.STORAGE_TYPE.__name__
        return defrag_type == kStringType and not self.isName

    # ------------------ Computation Helpers ----------------- #
    @staticmethod
    def full_blocks(empty_ids, total_blocks):
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
        # Get a list of all the IDs, it's range(1, total_blocks + 1) because
        # offsets go up to the total number of blocks
        all_ids = set(range(1, total_blocks + 1))
        return [i for i in all_ids if i not in empty_ids]

    @staticmethod
    def non_continuous_ids(ids):
        """
        Filters out continuous IDs from the list of IDs starting at 1.
        For example:
        Given: [1, 2, 3, 7, 8, 9]
        Filter out continuous: [1, 2, 3]
        Returns: ([1,2,3], [7, 8, 9])

        :param ids: List of IDs to filter
        :type ids: list[int]
        :return: Tuple with a list of cont. ids and a list of non-cont. ids
        :rtype: (list[int],list[int])
        """
        # We're 1-indexing since block 0 is always empty
        for idx, i in enumerate(sorted(ids), 1):
            if idx != i:
                return ids[:idx-1], ids[idx-1:]
        return ids, []

    @staticmethod
    def create_swap_table(full_non_cont_blocks, empty_blocks):
        """
        Creates a swap table mapping fragmented block IDs to their new
        destination

        :param full_non_cont_blocks: Sorted IDs of full non-continuous blocks
        :type full_non_cont_blocks: list[int]
        :param empty_blocks: Sorted list of IDs of empty blocks
        :type empty_blocks: list[int]
        :return: Dictionary of src->dest index maps for the swaps needed
        :rtype: dict[int,int]
        """
        # If we have no empty, blocks then there are no swaps to be done,
        # If we have no full non-continous blocks, there is no fragmentation.
        if not empty_blocks or not full_non_cont_blocks:
            return {}
        num_swaps = len(full_non_cont_blocks)
        new_slots = list(range(empty_blocks[0], empty_blocks[0] + num_swaps))
        return dict(zip(full_non_cont_blocks, new_slots))
