import sys
from colorama import Fore, Style


class PrettyPrinter:
    # Set when testing to avoid getting output with color escape sequences
    TESTING = False

    def __init__(self):
        """
        Initialize the colors used by the class, the instance handles all
        general printing.

        :return: Instance of pretty printer to use for output
        :rtype: PrettyPrinter
        """
        #TODO: change this to get themes from dict where NO_COLORS is a key
        # --- Color presets --- #
        # Color text green for the time to execute a command, make it dim
        self.timeFormat = Fore.GREEN + Style.DIM if not self.TESTING else ""
        # Color of the table with output
        self.tableColor = Fore.YELLOW if not self.TESTING else ""
        # Color of the header of the table
        self.headerColor = Fore.RED if not self.TESTING else ""
        # Color of the elements in the table
        self.elementColor = Fore.BLUE if not self.TESTING else ""
        # Color errors red, and make them bright
        self.errorFormat = Fore.RED + Style.BRIGHT if not self.TESTING else ""
        # Color help green
        self.helpColor = Fore.GREEN if not self.TESTING else ""
        # Color the info text white, make it bright
        self.infoFormat = Fore.WHITE + Style.BRIGHT if not self.TESTING else ""
        # End of color, reset to normal terminal color
        self.endFormat = Fore.RESET + Style.RESET_ALL if not self.TESTING else ""
             
        # --- Table Elements --- #
        self.pipeFormat = self.tableColor + "|" + self.endFormat
        self.pipeStartFormat = self.tableColor + "| " + self.endFormat
        self.pipeEndFormat = self.tableColor + " |" + self.endFormat
        self.dashFormat = self.tableColor + "-" + self.endFormat

    def print_list(self, lst, header=None, output=sys.stdout):
        max_len = max(map(len, lst))

        str_list = []
        # Format header
        if header is not None:
            max_len = max(max_len, len(header))
            str_list.append((max_len + 4) * self.dashFormat)
            str_list.append(self.pipeStartFormat + self.format_header(header.upper()) +
                            (max_len - len(header)) * " " + self.pipeEndFormat)
        str_list.append((max_len + 4) * self.dashFormat)
        for o in lst:
            new_o = self.format_element(o)
            str_list.append(self.pipeStartFormat + new_o +
                            (max_len - len(o)) * " " + self.pipeEndFormat)
        str_list.append((max_len + 4) * self.dashFormat)

        output.write("\n".join(str_list) + "\n")

    def print_table(self, table, header=None, output=sys.stdout):
        data = zip(*table)
        maxes = map(lambda l: max(map(lambda v: len(str(v)), l)), data)
        width = sum(m + 2 for m in maxes) + 2 + (len(maxes) - 1)
        # Format header
        if header is not None:
            maxes = [max(m, len(str(header[i] or ""))) for i, m in enumerate(maxes)]
            width = sum(m + 2 for m in maxes) + 2 + (len(maxes) - 1)
            output.write(width * self.dashFormat + "\n")
            # Apply color to header
            new_header = map(lambda h: self.format_header(h), header)
            # Output headers
            join_headers = self.pipeFormat.join(" %s%s " % (new_header[i], (maxes[i] - len(str(v))) * " ")
                                                for i, v in enumerate(header))
            output.write((self.pipeFormat + "%s" + self.pipeFormat + "\n") % join_headers)
        output.write(width * self.dashFormat + "\n")
        for row in table:
            # Apply color to rows
            new_row = map(lambda e: self.format_element(e), row)
            join_rows = self.pipeFormat.join(" %s%s " % (new_row[i], (maxes[i] - len(str(v))) * " ")
                                             for i, v in enumerate(row))
            output.write((self.pipeFormat + "%s" + self.pipeFormat + "\n")
                         % join_rows)
        output.write(width * self.dashFormat + "\n")

    def print_info(self, info, output=sys.stdout):
        """
        Pretty prints the given info text with the infoFormat field

        :param info: Information to print
        :type info: str
        :param output: Output stream
        :type output: FileIO[str]
        :return: Nothing
        :rtype: None
        """
        output.write(self.infoFormat + info + self.endFormat)

    def print_execute_time(self, start_time, end_time, output=sys.stdout):
        """
        Pretty prints the execution time with the timeFormat field

        :param start_time: Time when execution started
        :type start_time: float
        :param end_time: Time when execution ended
        :type end_time: float
        :return: Nothing
        :rtype: None
        """
        output.write((self.timeFormat + "Command executed in %.3fs"
                      + self.endFormat) % (end_time - start_time) + "\n")

    def print_help(self, help_str, output=sys.stdout):
        """
        Pretty prints the given help string with the helpColor field

        :param help_str: Help string to print
        :type help_str: str | FileIO[str]
        :return: Nothing
        :rtype: None
        """
        output.write(self.helpColor + help_str + self.endFormat + "\n")

    def print_error(self, error, output=sys.stdout):
        """
        Pretty prints the given error with the errorFormat field

        :param error: Prints the given error that responds to the str method
        :type error: Exception
        :return: Nothing
        :rtype: None
        """
        output.write(self.errorFormat + str(error) + self.endFormat + "\n")
    
    def format_header(self, header):
        """
        Formats the given header according to the headerColor field, and
        makes the headers uppercase.

        :param header: Header to format
        :type header: str
        :return: Formatted string
        :rtype: str
        """
        return self.headerColor + header.upper() + self.endFormat

    def format_element(self, element):
        """
        Formats the given element according to the elementColor field

        :param element: Row to format
        :type element: Any
        :return: String with format for given element
        :rtype: str
        """
        return self.elementColor + str(element) + self.endFormat
