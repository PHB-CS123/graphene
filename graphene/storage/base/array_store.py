from graphene.storage.base.array import *
from graphene.storage.base.property_store import *


class ArrayStore(GeneralStore):
    """
    Handles storage of arrays to a file. It stores the arrays using
    the format:
    (inUse, type, previousBlock, amount, nextBlock, data)
    String arrays are stored as an array of integers where the integers refer
    to the starting position of the string in a StringStore
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'B': unsigned char
    # 'I': unsigned int
    HEADER_STRUCT_FORMAT_STR = "= ? B I I I"
    ''':type str'''

    # Size of header struct (bytes)
    HEADER_SIZE = struct.calcsize(HEADER_STRUCT_FORMAT_STR)
    ''':type int'''

    # --------------- Array Types --------------- #
    # Format string to handle bool types (1 byte)
    # '?': boolean
    BOOL_FORMAT_STR = "?"
    ''':type: str'''

    # Format string to handle char types (2 bytes)
    # 'H': unsigned short
    CHAR_FORMAT_STR = "H"
    ''':type: str'''

    # Format string used to handle short types (2 bytes)
    # 'h': signed short
    SHORT_FORMAT_STR = 'h'
    ''':type: str'''

    # Format string used to handle int and string ID types (4 bytes)
    # 'i': signed int
    INT_FORMAT_STR = "i"
    ''':type: str'''

    # Format string used to handle float types (4 bytes)
    # 'f': float
    FLOAT_FORMAT_STR = "f"
    ''':type: str'''

    # Format string used to handle long types (8 bytes)
    # 'q': signed long long
    LONG_FORMAT_STR = "q"
    ''':type: str'''

    # Format string to handle double types (8 bytes)
    # 'd': double
    DOUBLE_FORMAT_STR = "d"
    ''':type: str'''
    # ------------------------------------------- #

    # Padding tuple for non-full array blocks
    PAD_TUPLE = (0,)

    # Name of ArrayStore File
    FILE_NAME = "graphenestore.arraystore.db"
    ''':type str'''

    def __init__(self, block_size=40):
        """
        Creates an ArrayStore instance which handles reading/writing to the
        file containing array values

        :param block_size: Maximum size of the array block (multiple of 8)
        :type block_size: int
        :return: Array store instance for handling array records
        :rtype: ArrayStore
        """
        if block_size % 8 != 0:
            raise ValueError("Block size for array store must be multiple of 8")

        # Store the given block size
        self.blockSize = block_size

        # Size of record will be the size of the header and the block itself
        record_size = self.HEADER_SIZE + block_size

        # Initialize using generic base class
        super(ArrayStore, self).__init__(self.FILE_NAME, record_size)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates an array object from the given packed data

        :param index: Index of the array the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: Array from packed data
        :rtype: Array
        """
        # Split the packed data into header and block
        header_data = packed_data[:self.HEADER_SIZE]
        block_data = packed_data[self.HEADER_SIZE:]

        # Unpack the header data using the header struct format
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        unpacked_header_data = header_struct.unpack(header_data)

        # Get the property header components
        in_use = unpacked_header_data[0]
        array_type = Property.PropertyType(unpacked_header_data[1])
        previous_block = unpacked_header_data[2]
        amount = unpacked_header_data[3]
        next_block = unpacked_header_data[4]

        # Empty data, deleted item
        if in_use is False and array_type == Property.PropertyType.undefined \
           and previous_block == 0 and amount == 0 and next_block == 0:
            return None

        # Unpack the block data
        items = self.items_from_data(array_type, block_data, amount)
        return Array(index, in_use, array_type, previous_block, amount,
                     next_block, items)

    def packed_data_from_item(self, item):
        """
        Creates packed data with the array given

        :param item: Item to convert into packed data
        :type item: Array
        :return: Packed data
        :rtype: bytes
        """
        # Pack the array header into a struct with the order
        # (inUse, type, previousBlock, amount, nextBlock)
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        packed_header = header_struct.pack(item.inUse, item.type.value,
                                           item.previousBlock, item.amount,
                                           item.nextBlock)
        # Pack the data block
        packed_block = self.items_to_data(item.type, item.items)
        # Concatenate the two
        return packed_header + packed_block

    def items_from_data(self, array_type, packed_data, amount):
        """
        Get the array items from the given packed data

        :param array_type: Type of array items
        :type array_type: PropertyType
        :param packed_data: Packed data to convert to items
        :type packed_data: bytes
        :param amount: Number of items expected in the array
        :type amount: int
        :return: Array of items of array type
        :rtype: list
        """
        # Get the size and format string from the given array type
        (size, format_str) = self.size_and_format_str_for_type(array_type)

        # Get the items with the size and format string determined
        items = self.list_from_data(packed_data, format_str,
                                    self.blockSize, size, amount)

        # Convert the array of unsigned shorts to actual unicode chars
        if array_type is Property.PropertyType.charArray:
            return map(lambda x: unichr(x), items)
        else:
            return items

    def items_to_data(self, array_type, items):
        """
        Pack the given items using the appropriate struct format string

        :param array_type: Array type of the items
        :type array_type: PropertyType
        :param items: Items to pack with the given type
        :type items: list
        :return: Packed data
        :rtype: bytes
        """
        if array_type is Property.PropertyType.charArray:
            items = map(lambda x: ord(x), items)
        # Get the size and format string from the given array type
        (size, format_str) = self.size_and_format_str_for_type(array_type)
        # Pack the items
        return self.list_to_data(items, format_str, self.blockSize, size)

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed struct of 0s
        :rtype: bytes
        """
        # Create an empty header struct
        empty_header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        packed_header = empty_header_struct.pack(0, 0, 0, 0, 0)

        # Create an empty data payload (using BOOL_FORMAT_STR for easy padding)
        empty_data = struct.Struct(self.BOOL_FORMAT_STR * self.blockSize)
        pad_tuple = self.blockSize * self.PAD_TUPLE
        packed_payload = empty_data.pack(*pad_tuple)

        # Concatenate header and payload
        return packed_header + packed_payload

    @classmethod
    def size_and_format_str_for_type(cls, array_type):
        """
        Get the size and structure format string for the given array type

        :param array_type: Array type to get size and format string for
        :type array_type: PropertyType
        :return: Tuple with size and format string
        :rtype: tuple
        """
        if array_type is Property.PropertyType.boolArray:
            size = 1
            format_str = cls.BOOL_FORMAT_STR
        elif array_type is Property.PropertyType.charArray:
            size = 2
            format_str = cls.CHAR_FORMAT_STR
        elif array_type is Property.PropertyType.shortArray:
            size = 2
            format_str = cls.SHORT_FORMAT_STR
        elif array_type is Property.PropertyType.floatArray:
            size = 4
            format_str = cls.FLOAT_FORMAT_STR
        elif array_type is Property.PropertyType.longArray:
            size = 8
            format_str = cls.LONG_FORMAT_STR
        elif array_type is Property.PropertyType.doubleArray:
            size = 8
            format_str = cls.DOUBLE_FORMAT_STR
        elif array_type is Property.PropertyType.intArray or \
                array_type is Property.PropertyType.stringArray:
            size = 4
            format_str = cls.INT_FORMAT_STR
        else:
            raise ValueError("Invalid array type.")

        return size, format_str

    @classmethod
    def capacity_for_type(cls, array_type, block_size):
        """
        Get the number of items that an array block with the given block size
        can store for the given item type

        :param array_type: Type of array
        :type array_type: PropertyType
        :param block_size: Size of array block
        :type block_size: int
        :return: Capacity for given block size and type
        :rtype: int
        """
        (size, format_str) = cls.size_and_format_str_for_type(array_type)
        return block_size / size

    @classmethod
    def list_to_data(cls, array, format_str, block_size, type_size):
        """
        Create packed data from the given array and parameters

        :param array: List of items to pack
        :type array: list
        :param format_str: Format string for types in list
        :type format_str: str
        :param block_size: Size of data block
        :type block_size: int
        :param type_size: Size of types in list
        :type type_size: int
        :return: Packed data
        :rtype: bytes
        """
        # Calculate the number of items in struct
        amt_struct_items = block_size / type_size
        # Create a structure depending on the block size & type size
        # For example, if the block size is 16, then it can store:
        # 2 doubles or longs (8 bytes)
        # 4 ints, floats, or string IDs (4 bytes)
        # 8 shorts or chars (unicode) (2 bytes)
        # 16 booleans (1 byte)
        total_format_str = format_str * amt_struct_items
        s = struct.Struct(total_format_str)
        # Pad the missing items with the pad tuple
        amt_missing = (amt_struct_items - len(array))
        padded_items = tuple(array) + cls.PAD_TUPLE * amt_missing
        # Pack the items
        return s.pack(*padded_items)

    @staticmethod
    def list_from_data(packed_data, format_str, block_size, type_size, amount):
        """
        Create a list of items from the given packed data and parameters

        :param packed_data: Packed data to get items from
        :type packed_data: bytes
        :param format_str: Format string corresponding to the data type
        :type format_str: str
        :param block_size: Size of block
        :type block_size: int
        :param type_size: Size of type (1, 2, 4, or 8 bytes)
        :type type_size: int
        :param amount: Amount of items expected in the array
        :type amount: int
        :return: Array of items
        :rtype: list
        """
        # Create a structure depending on the block size & type size
        # For example, if the block size is 16, then it can store:
        # 2 doubles or longs (8 bytes)
        # 4 ints, floats, or string IDs (4 bytes)
        # 8 shorts or chars (unicode) (2 bytes)
        # 16 booleans (1 byte)
        total_format_str = format_str * (block_size / type_size)
        s = struct.Struct(total_format_str)
        unpacked_array = s.unpack(packed_data)
        # Truncate the array to remove padded items
        return list(unpacked_array[:amount])