from Shell import Shell
from server.GrapheneServer import GrapheneServer

server = GrapheneServer()

shell = Shell(server)
shell.cmdloop()
