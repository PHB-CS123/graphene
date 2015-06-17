from graphene.client.shell import Shell
from graphene.server.server import GrapheneServer
from graphene.utils.gp_logging import *

if __name__ == "__main__":
    server = GrapheneServer()

    shell = Shell(server)
    # Initialize logger with config file
    GPLogging()
    # Begin command loop
    shell.cmdloop()
