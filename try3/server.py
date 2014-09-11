#!/usr/bin/env python3

import socketserver
import select
import configparser


# Listen on a port
# If a client starts sending packages, echo them to all other clients
class RequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):

        self.config = configparser.ConfigParser()
        self.config.read("settings.conf")

        self.start_buffer_size = int(self.config["DEFAULT"]["BufferSize"])
        self.buffer_size = 0
        self.buffer = bytearray(0)
        self.pointer = 0

        self.sender = False
        self.running = False

        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def recvExact(self, buffer_size):
        pointer = 0
        buffer = bytearray(buffer_size)
        while pointer < buffer_size:
            data = self.request.recv(buffer_size - pointer)
            if not data:
                print("[%s %s] Removing Client" % self.client_address)
                self.running = False
                return

            buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return buffer

    def handle(self):
        print("[%s %s] Added new Client" % self.client_address)

        # Herausfinden, ob es sich um einen Sender handelt

        data = self.request.recv(self.start_buffer_size)

        if data:
            if data.startswith(b"sender"):
                self.sender = True

                self.buffer_size = int(data[6:])
                self.buffer = bytearray(self.buffer_size)

                self.request.sendall(b"ok")
                self.running = True
                print("[%s %s] New Client is Sender" % self.client_address)

            elif data.startswith(b"receiver"):
                self.sender = False
                self.running = True
                print("[%s %s] New Client is Receiver" % self.client_address)

            else:
                print("[%s %s] Do not understand new Client!" % self.client_address)
                self.running = False
                return

        else:
            print("[%s %s] New Client does not respond!" % self.client_address)
            self.running = False
            return

        if self.sender:
            while self.running:
                self.buffer = self.recvExact(self.buffer_size)

        else:
            while self.running:
                pass

"""
    def reading_clients(self, reading_sockets):

        for sock in reading_sockets:
            if sock == 0:
                pass
            elif sock == self.socket:
                comm, address = self.socket.accept()
                self.client_list.append(comm)
                print(self.client_list)
                print("New Client", address)
            else:
                # Call first sender the sender and recv buffer_size
                if self.sender == 0:
                    data = sock.recv(self.start_buffer_size)
                    if data:
                        self.buffer_size = int(data[:data.find(b"f")])
                        self.buffer = bytearray(self.buffer_size)
                        self.client_list.remove(sock)
                        self.sender = sock
                        print("New Sender", sock.getpeername(), self.buffer_size)
                # Accept every other message from him
                elif self.sender == sock:
                    pointer = 0
                    while pointer < self.buffer_size:
                        data = sock.recv(self.buffer_size - pointer)
                        if not data:
                            self.sender = 0
                            print("Remove Sender", sock.getpeername())
                            sock.close()
                            self.buffer_size = 0

                        self.buffer[pointer:pointer + len(data)] = data
                        pointer += len(data)
                # But not from others!
                else:
                    data = sock.recv(self.start_buffer_size)
                    if data:
                        print("Client trying to write", sock.getpeername())
                    else:
                        print("Client says goodbye", sock.getpeername())

                    sock.close()
                    self.client_list.remove(sock)

    def writing_clients(self, writing_sockets):
        if len(writing_sockets) > 0:
            print(writing_sockets)
        for sock in writing_sockets:
            if sock != self.socket:
                sock.sendall(self.buffer)

    def accept(self):
        try:
            while True:
                reading_sockets, writing_sockets, _ = select.select([self.socket] +
                                                                    self.client_list + [self.sender], [], [])

                self.reading_clients(reading_sockets)
                self.writing_clients(writing_sockets)

        except KeyboardInterrupt:
            print("Closing")

        finally:
            for client in self.client_list:
                client.close()
            self.socket.close()"""


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("settings.conf")

    try:
        socketserver.ThreadingTCPServer(("", int(config["DEFAULT"]["Port"])), RequestHandler).serve_forever()
    except KeyboardInterrupt:
        pass

