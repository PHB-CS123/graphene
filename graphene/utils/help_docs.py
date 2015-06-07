from graphene.utils.pretty_printer import PrettyPrinter

import os
import logging

class HelpDocs:
    # Directory containing documentation for commands
    DOCS_FOLDER = "graphene/utils/help-docs/"
    # Aliases in the help documentation will be separated by this character
    # For example: Exit-Quit.txt
    ALIAS_DELIMETER = "-"

    def __init__(self):
        # Get a logger to print logging output to
        self.logger = logging.getLogger(self.__class__.__name__)
        # Get names of help files
        help_files = self.get_help_filenames()
        self.helpFiles = sorted(help_files)
        # Get topics from the filenames of the help files
        self.topics = self.topics_from_filenames(help_files)

    def print_help_topic(self, topic):
        """
        Prints the documentation for the given help topic

        :param topic: Help topic to print documentation for
        :type topic: str
        :return: Nothing
        :rtype: None
        """
        filename = self.get_filename_from_topic(topic)
        # Return if no file for topic
        if not filename:
            return
        # Try opening the file
        try:
            help_file = open(self.DOCS_FOLDER + filename, "r")
        except IOError:
            self.logger.warn("Help file deleted while program running "
                             "for topic: %s" % topic)
            return
        # Print the contents of the file using PrettyPrinter
        printer = PrettyPrinter()
        printer.print_help(help_file.read())

    def get_help_filenames(self):
        """
        Returns a list with the filenames of the help files

        :return: List with names of help files
        :rtype: list[str]
        """
        try:
            return os.listdir(self.DOCS_FOLDER)
        except OSError:
            self.logger.warn("Invalid help docs. folder: %s", self.DOCS_FOLDER)
            return None

    def topics_from_filenames(self, files):
        """
        Get the formatted topics list from the given file names

        :param files: File names of help topics
        :type files: list[str]
        :return: Formatted list of topics
        :rtype: list[str]
        """
        topics = []
        for filename in files:
            # Strip file extension
            topic = os.path.splitext(filename)[0]
            # Split the name on the alias delimeter
            aliases = topic.split(self.ALIAS_DELIMETER)
            # Add topic (and possible aliases) to the topics list
            topics.extend(aliases)
        return topics

    def get_filename_from_topic(self, topic):
        """
        Returns the filename for the file with the given help topic

        :param topic: Topic to get help filename for
        :type topic: str
        :return: Filename of help file
        :rtype: str
        """
        for filename in self.helpFiles:
            # Topic in filename
            if topic in filename:
                return filename
        return None