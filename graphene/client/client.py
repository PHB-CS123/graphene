from Shell import Shell
from graphene.server.GrapheneServer import GrapheneServer

if __name__ == "__main__":
    server = GrapheneServer()

    shell = Shell(server)
    shell.cmdloop()
