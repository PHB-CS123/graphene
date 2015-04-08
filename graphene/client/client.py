from Shell import Shell
from graphene.server.GrapheneServer import GrapheneServer

server = GrapheneServer()

shell = Shell(server)
shell.cmdloop()
