import sys
import logging
from colorama import Fore, Style

class SyntaxHighlighting:
    # TODO: get keywords from .g4 file in the future
    KEYWORDS_FILENAME = "graphene/utils/keywords.txt"
    COMMENT_IDENTIFIER = "#"
    # TODO: eliminate "o", added to prevent into from highlighting "int"
    BLACKLIST = ["_", "o"]
    # TODO: eliminate duplicate symbols ");" , ");\"" "),"
    # TODO: figure out how to highlight "\"" and "["
    SYMBOLS = ["->", "<=", ">=", ");", "),", ");", "(", ")", ":", "|", ";",
               "=", ",", "-", "<", ">"]
    # Property types available, NOTE: arrays are put first so they are detected
    # when doing syntax highlighting before primitives.
    TYPES = ["int[]", "long[]", "bool[]", "short[]", "char[]", "float[]",
             "double[]", "string[]", "int", "long", "bool", "short", "char",
             "float", "double", "string"]

    def __init__(self, keyword_color, symbol_color, type_color):
        self.logger = self.logger = logging.getLogger(self.__class__.__name__)
        self.keywords = self.get_keywords()
        # --- Syntax Colors --- #
        self.keywordColor = keyword_color
        self.symbolColor = symbol_color
        self.typeColor = type_color

    def get_keywords(self):
        """
        Get the keywords from the keywords file

        :return: List of keywords
        :rtype: list[str]
        """
        try:
            syntax_file = open(self.KEYWORDS_FILENAME, "r")
        except IOError:
            self.logger.warn("Unable to open syntax file: %s"
                             % self.KEYWORDS_FILENAME)
            return None

        keywords = []
        for line in syntax_file:
            # Strip whitespace
            line = line.strip()
            # Comment, skip
            if line.startswith(self.COMMENT_IDENTIFIER):
                continue
            # Split by commas, remove whitespace, filter any empty strings
            keywords.extend(map(lambda x: x.strip(), line.split(",")))
            keywords = filter(lambda x: x != "", keywords)

        return sorted(keywords)

    def highlight(self, line, existing_color=""):
        """
        Apply syntax highlighting to the given line, if the line has an
        existing color, pass it

        :param line: Line to apply highlighting to
        :type line: str
        :param existing_color: Color the line currently has
        :type existing_color: str
        :return: New line with syntax highlighting
        :rtype: str
        """
        new_line = ""
        for i, word in enumerate(line.split(" ")):
            #TODO: highlight multiple symbols on the same word i.e. (a:
            # Symbols must be highlighted before anything because [ and ]
            # are possible symbols, but also escape sequences for colors
            word = self.highlight_id(word, self.SYMBOLS,
                                     self.symbolColor, existing_color)
            word = self.highlight_id(word, self.keywords,
                                     self.keywordColor, existing_color)
            word = self.highlight_id(word, self.TYPES,
                                     self.typeColor, existing_color)
            # Add formatted word to new string
            new_line += word
            # Add space back
            new_line += " "
        return new_line

    def highlight_id(self, word, identifiers, color, e_color=""):
        """
        Apply syntax highlighting to identifiers

        :param word: Word to apply highlighting to
        :type word: str
        :param identifiers: Items to highlight
        :type identifiers: list[str]
        :param e_color: Existing color to return to after highlighting
        :type e_color: str
        :return: Highlighted keyword, or regular if it doesn't need highlighting
        :rtype: str
        """
        new_word = None
        # Check if current word contains keyword
        for keyword in identifiers:
            # Keyword length
            k_len = len(keyword)
            loc = word.find(keyword)
            # Keyword found
            if loc != -1:
                # If a word in the blacklist follows, it's not a keyword
                # e.g SHOW_ALL shouldn't be highlighted
                # If a word in the blacklist is before, it's not a keyword
                # e.g. PRINT_RELATION shouldn't be highlighted
                if (loc + k_len < len(word) and
                        word[loc + k_len] in self.BLACKLIST) or \
                        (loc != 0 and word[loc - 1] in self.BLACKLIST):
                    continue
                # Where to end syntax
                end_s = loc + k_len
                new_word = self.color_item(word, color, loc, end_s, e_color)
                # Word highlighted, stop searching for keywords
                break
        # Return highlighted word or original if no highlighting was applied
        return new_word or word

    def color_item(self, item, color, start, stop, e_color):
        """
        Color the given item

        :param item: Item to color
        :type item: str
        :param color: Color to apply
        :type color: str
        :param start: Start coloring
        :type start: int
        :param stop: End coloring
        :type stop: int
        :param e_color: Existing color to return to after the highlighting
        :type e_color: str
        :return: Colored item
        :rtype: str
        """
        return item[:start] + color + item[start:stop] + e_color + item[stop:]


class PrettyPrinter:
    # Set when testing to avoid getting output with color escape sequences
    NO_COLORS = False

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
        self.timeFormat = Fore.GREEN + Style.DIM if not self.NO_COLORS else ""
        # Color of the table with output
        self.tableColor = Fore.YELLOW if not self.NO_COLORS else ""
        # Color of the header of the table
        self.headerColor = Fore.RED if not self.NO_COLORS else ""
        # Color of the elements in the table
        self.elementColor = Fore.BLUE if not self.NO_COLORS else ""
        # Color errors red, and make them bright
        self.errorFormat = Fore.RED + Style.BRIGHT if not self.NO_COLORS else ""
        # Color help green
        self.helpColor = Fore.GREEN if not self.NO_COLORS else ""
        # Color the info text white, make it bright
        self.infoFormat = Fore.WHITE + Style.BRIGHT if not self.NO_COLORS else ""

        # Format for keyword highlighting
        self.keywordFormat = Fore.RED if not self.NO_COLORS else ""
        # Format for symbol highlighting
        self.symbolFormat = Fore.WHITE if not self.NO_COLORS else ""
        # Format for type highlighting
        self.typeFormat = Fore.CYAN if not self.NO_COLORS else ""

        # End of color, reset to normal terminal color
        self.endFormat = Fore.RESET + Style.RESET_ALL if not self.NO_COLORS else ""

        # --- Table Elements --- #
        self.pipeFormat = self.tableColor + "|" + self.endFormat
        self.pipeStartFormat = self.tableColor + "| " + self.endFormat
        self.pipeEndFormat = self.tableColor + " |" + self.endFormat
        self.dashFormat = self.tableColor + "-" + self.endFormat

        # Syntax highlighting
        self.syntaxH = SyntaxHighlighting(self.keywordFormat, self.symbolFormat,
                                          self.typeFormat)

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
        # If a syntax color is set, highlight syntax
        if self.keywordFormat or self.symbolFormat or self.typeFormat:
            help_str = self.syntaxH.highlight(help_str, self.helpColor)
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
