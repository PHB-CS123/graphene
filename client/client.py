from Shell import Shell
from server.GrapheneServer import GrapheneServer
import readline

server = GrapheneServer()

shell = Shell(server)
shell.cmdloop()
