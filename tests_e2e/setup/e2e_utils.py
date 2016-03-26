from StringIO import StringIO
from difflib import unified_diff

from graphene.storage.base.graphene_store import GrapheneStore
from tests_e2e.setup.server_ext import GrapheneTestServer


class E2EUtils:
    END_OF_COMMAND = ";"
    LINE_COMMENT = "#"
    START_BLOCK_COMMENT = "/*"
    END_BLOCK_COMMENT = "*/"

    def __init__(self):
        GrapheneStore.TESTING = True
        self.testServer = GrapheneTestServer()
        # Previous output by the server
        self.previousOutputIO = None
        # Previous command
        self.previousCommand = None

    def __str__(self):
        return "Command: %s\n\n Output:\n%s" \
               % (self.previousCommand, self.previousOutputIO.getvalue())

    def do_command(self, command):
        self.clear_buffer()
        self.previousCommand = command
        self.testServer.do_test_command(command, self.previousOutputIO)

    def do_command_cmp(self, command, old_out, print_diff=True):
        """
        Runs the given command and compares the output to the given output string

        :param command: Command to run and capture output for
        :type command: str
        :param old_out: Old command output
        :type old_out: str
        :param print_diff: Whether differences in output should be printed
        :type print_diff: bool
        :return: True if the results were the same, False otherwise
        :rtype: bool
        """
        s, _ = self._do_command_cmp(command, old_out, print_diff)
        return s

    def re_run_previous_command(self, print_diff=True):
        """
        Runs the previously-run command and compares output to the old output

        :param print_diff: Whether differences in output should be printed
        :type print_diff: bool
        :return: True if the results were the same, False otherwise
        :rtype: bool
        """
        s, n_io = self._do_command_cmp(self.previousCommand,
                                       self.previousOutputIO.getvalue(),
                                       print_diff)
        self.replace_old_output_io(n_io)
        return s

    def _do_command_cmp(self, cmd, previous_output, print_diff=True):
        """
        Runs the previous command again and compares the output

        :param cmd: Command to run and capture output for
        :type cmd: str
        :param previous_output: Output string of previous command to compare
        :type previous_output: str
        :param print_diff: Whether differences in output should be printed
        :type print_diff: bool
        :return: True if the results were the same, False otherwise along with
                 the result of re-running the command
        :rtype: tuple(bool, StringIO)
        """
        new_output_io = StringIO()
        self.testServer.do_test_command(cmd, new_output_io)
        new_output = new_output_io.getvalue()
        same = new_output == previous_output
        if print_diff:
            if same:
                print "Command returned the same output."
            else:
                self.print_diff(previous_output, new_output)
        return same, new_output_io

    def replace_old_output_io(self, new_output_io):
        if self.previousOutputIO:
            self.previousOutputIO.close()
        self.previousOutputIO = new_output_io

    def clear_buffer(self):
        if self.previousOutputIO:
            self.previousOutputIO.close()
        self.previousOutputIO = StringIO()
        self.previousCommand = None

    @staticmethod
    def print_diff(prev, new):
        prev = prev.strip().splitlines()
        new = new.strip().splitlines()
        for line in unified_diff(prev, new, fromfile='previous',
                                 tofile='new', lineterm=''):
            print line

    @classmethod
    def commands_from_file(cls, filename):
        commands = []  # List of parsed commands
        command = ""  # Current command
        is_block_comment = False  # True if we're within a block comment
        setup_file = open(filename)
        for line in setup_file.readlines():
            # --- Handle block comments --- #
            block_comment_start_loc = line.find(cls.START_BLOCK_COMMENT)
            block_comment_end_loc = line.find(cls.END_BLOCK_COMMENT)
            if block_comment_start_loc != -1:
                # One line block comment, remove it
                if block_comment_end_loc != -1:
                    end = block_comment_end_loc + len(cls.END_BLOCK_COMMENT)
                    line = line.replace(line[block_comment_start_loc:end], "")
                    block_comment_end_loc = -1
                else:
                    line = line[:block_comment_start_loc]
                    is_block_comment = True
            # We're within a block comment, no ending comment delimeter
            if block_comment_end_loc == -1 and is_block_comment:
                continue
            # Process any command after the end of the comment block
            elif block_comment_end_loc != -1:
                line = line[block_comment_end_loc + len(cls.END_BLOCK_COMMENT):]
                is_block_comment = False
            # --- Handle one-line comments --- #
            line_comment_loc = line.find(cls.LINE_COMMENT)
            if line_comment_loc != -1:
                line = line[:line_comment_loc]
            # --- Handle regular command --- #
            command += cls.process_line(line)
            if command.find(cls.END_OF_COMMAND) != -1:
                commands.append(command.strip())
                command = ""
        setup_file.close()
        return commands

    @staticmethod
    def process_line(line):
        """
        Removes newlines from the given line

        :param line: Line to process
        :type line: str
        :return: Processed line
        :rtype: str
        """
        return line.replace("\n", " ")
