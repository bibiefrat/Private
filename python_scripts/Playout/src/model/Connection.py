import socket


class Connection(object):
    def __init__(self,server,port):
        self.server = server
        self.port = port
        self.connection_socket = None
#        self.Connect()

    def SetServerPort(self,serverPort):
        self.server,port = serverPort.split(":")
        self.port = int(port)

    def Connect(self):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_socket.connect((str(self.server), self.port))
        print "connected"