import sys
from colorama import Fore


class PrettyPrinter:
    # --- Color presets --- #
    # Color of the text for the time it took to execute a command
    TIME_COLOR = Fore.GREEN
    # Color of the table with output
    TABLE_COLOR = Fore.YELLOW
    # Color of the header of the table
    HEADER_COLOR = Fore.RED
    # Color of the elements in the table
    ELEMENT_COLOR = Fore.BLUE
    # End of color, reset to normal terminal color
    END = Fore.RESET

    # Table Elements
    PIPE = TABLE_COLOR + "|" + END
    PIPE_START = TABLE_COLOR + "| " + END
    PIPE_END = TABLE_COLOR + " |" + END
    DASH = TABLE_COLOR + "-" + END

    @classmethod
    def print_list(cls, lst, header=None, output=sys.stdout):
        max_len = max(map(len, lst))

        str_list = []
        # Format header
        if header is not None:
            max_len = max(max_len, len(header))
            str_list.append((max_len + 4) * cls.DASH)
            str_list.append(cls.PIPE_START + cls.format_header(header.upper()) +
                            (max_len - len(header)) * " " + cls.PIPE_END)
        str_list.append((max_len + 4) * cls.DASH)
        for o in lst:
            str_list.append(cls.PIPE_START + o + (max_len - len(o)) * " " + cls.PIPE_END)
        str_list.append((max_len + 4) * cls.DASH)

        output.write("\n".join(str_list) + "\n")

    @classmethod
    def print_table(cls, table, header=None, output=sys.stdout):
        data = zip(*table)
        maxes = map(lambda l: max(map(lambda v: len(str(v)), l)), data)
        width = sum(m + 2 for m in maxes) + 2 + (len(maxes) - 1)
        # Format header
        if header is not None:
            maxes = [max(m, len(str(header[i] or ""))) for i, m in enumerate(maxes)]
            width = sum(m + 2 for m in maxes) + 2 + (len(maxes) - 1)
            output.write(width * cls.DASH + "\n")
            # Apply color to header
            new_header = map(lambda h: cls.format_header(h), header)
            # Output headers
            join_headers = cls.PIPE.join(" %s%s " % (new_header[i], (maxes[i] - len(str(v))) * " ")
                                         for i, v in enumerate(header))
            output.write((cls.PIPE + "%s" + cls.PIPE + "\n") % join_headers)
        output.write(width * cls.DASH + "\n")
        for row in table:
            # Apply color to rows
            new_row = map(lambda e: cls.format_element(e), row)
            join_rows = cls.PIPE.join(" %s%s " % (new_row[i], (maxes[i] - len(str(v))) * " ")
                                      for i, v in enumerate(row))
            output.write((cls.PIPE + "%s" + cls.PIPE + "\n") % join_rows)
        output.write(width * cls.DASH + "\n")

    @classmethod
    def print_execute_time(cls, start_time, end_time):
        """
        Pretty prints the execution time

        :param start_time: Time when execution started
        :type start_time: float
        :param end_time: Time when execution ended
        :type end_time: float
        :return: Nothing
        :rtype: None
        """
        print((Fore.GREEN+"Command executed in %.3fs"+Fore.RESET)
              % (end_time - start_time))

    @classmethod
    def format_header(cls, header):
        """
        Formats the given header according to the HEADER_COLOR field, and makes
        the headers uppercase.

        :param header: Header to format
        :type header: str
        :return: Formatted string
        :rtype: str
        """
        return cls.HEADER_COLOR + header.upper() + cls.END

    @classmethod
    def format_element(cls, element):
        """
        Formats the given element according to the ELEMENT_COLOR field

        :param element: Row to format
        :type element: Any
        :return: String with format for given element
        :rtype: str
        """
        return cls.ELEMENT_COLOR + str(element) + cls.END

