from StringIO import StringIO
from difflib import unified_diff

from tests_e2e.setup.server_ext import GrapheneTestServer


class E2EUtils:
    def __init__(self):
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

    def re_run_previous_command(self, print_diff=True):
        """
        Runs the previous command again and compares the output

        :return: True if the results were the same, False otherwise
        :rtype: bool
        """
        new_output_io = StringIO()
        self.testServer.do_test_command(self.previousCommand, new_output_io)
        new_output = new_output_io.getvalue()
        old_output = self.previousOutputIO.getvalue()
        same = new_output == old_output
        if print_diff:
            if same:
                print "Command returned the same output."
            else:
                self.print_diff(old_output, new_output)
        self.replace_old_output_io(new_output_io)
        return same

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
