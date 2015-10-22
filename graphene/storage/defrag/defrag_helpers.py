import sys

from graphene.storage.base.general_store import EOF
from graphene.storage.defrag.reference_map import offset_descriptor_for_class
from graphene.utils import PrettyPrinter


class FilePrinter:
    def __init__(self, base_store, header=False, type_desc=False,
                 record_offset=False, item_index=False):
        """
        Initializes a file printer for the given base store

        :param base_store: Base store to print items of
        :type base_store: GeneralStore
        :param header: Include item description in the header
        :type header: bool
        :param type_desc: Include item type description
        :type type_desc: bool
        :param record_offset: Include the record type offset
        :param record_offset: bool
        :param item_index: Include record index
        :type item_index: bool
        :return: File printer used to print file items
        :rtype: FilePrinter
        """
        # Base store
        self.baseStore = base_store
        # Offset descriptor
        self.offsetDescriptor = \
            offset_descriptor_for_class(base_store.STORAGE_TYPE)
        # File pretty printer
        self.printer = PrettyPrinter()
        # Print options
        self.header = header
        self.typeDesc = type_desc
        self.recordOffset = record_offset
        self.itemIndex = item_index

    def print_blocks(self, start=1, max_blocks=25, output=sys.stdout):
        """
        Prints the data blocks starting at the given index.

        :param start: Index to start block printing at
        :type start: int
        :param max_blocks: Number of blocks to print
        :type max_blocks: int
        :param output: Output destination
        :type output: FileIO[str]
        :return: Nothing
        :rtype: None
        """
        values = []
        # Get record values
        for i in range(start, max_blocks):
            record = self.baseStore.item_at_index(i)
            if record is EOF:
                break
            list_record = [i] + record.list() \
                if self.itemIndex else record.list()
            values.append(list_record)
        headers = None
        if self.header:
            headers = ["Index"] if self.itemIndex else []
            # Get header values
            for offset, desc in self.offsetDescriptor.items():
                header = ""
                # Append the offset for this record type
                if self.recordOffset:
                    header += str(offset) + ": "
                header += desc[0]
                if self.typeDesc:
                    header += " (" + desc[0] + ")"
                headers.append(header)
        self.printer.print_table(values, header=headers, output=output)
