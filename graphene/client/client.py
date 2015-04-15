from graphene.client.shell import Shell
from graphene.server.server import GrapheneServer

if __name__ == "__main__":
    server = GrapheneServer()

    shell = Shell(server)
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        pass
