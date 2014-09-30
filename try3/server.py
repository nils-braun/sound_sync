#!/usr/bin/env python3

import socketserver
import select
import configparser

start_buffer_size = 0
buffer_size = 0


class ServerInterface:
    def __init__(self):
        self.sender = 0
        self.listener = list()
        self.listener_buffer_number = list()
        self.buffers = list()
        self.start_pointer = 0
        self.end_pointer = 0
        self.buffer_size = 10

    def add_sender(self, sender):
        if self.sender == 0:
            self.sender = sender
        else:
            print("[Server] New sender!")
            self.sender = sender

    def add_listener(self, listener):
        self.listener.append(listener)
        self.listener_buffer_number.append(self.start_pointer)

    def add_buffer(self, buffer):
        self.buffers.append(buffer)
        self.end_pointer += 1
        if len(self.buffers) > self.buffer_size:
            self.buffers.pop(0)
            self.start_pointer += 1

    def get_buffer(self, listener):
        index = self.listener_buffer_number[self.listener.index(listener)] - self.start_pointer
        if index < 0:
            self.listener_buffer_number[self.listener.index(listener)] = self.start_pointer + 1
            return self.buffers[0]
        elif index >= self.end_pointer - self.start_pointer:
            return 0
        else:
            self.listener_buffer_number[self.listener.index(listener)] += 1
            return self.buffers[index]

    def is_sender(self, sender):
        return self.sender is sender

    def is_empty(self):
        return self.end_pointer == 0

serverInterface = ServerInterface()


# Listen on a port
# If a client starts sending packages, echo them to all other clients
class RequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):

        self.sender = False
        self.running = False

        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def recv_exact(self):
        pointer = 0
        tmp_buffer = bytearray(buffer_size)
        while pointer < buffer_size:
            data = self.request.recv(buffer_size - pointer)
            if not data:
                print("[%s %s] Removing Client" % self.client_address)
                self.running = False
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    # this function is called everytime a new client wants to get access to the server
    def handle(self):

        global buffer_size

        print("[%s %s] Added new Client" % self.client_address)

        # Receive first message to switch between sender and listener
        data = self.request.recv(start_buffer_size)

        if data:
            if data.startswith(b"sender"):
                print("[%s %s] New Client is Sender" % self.client_address)

                buffer_size = (4*int(data[len("sender"):]))
                print("[Server] buffer_size: %d" % buffer_size)

                self.request.sendall(b"ok")

                serverInterface.add_sender(self)

                self.running = True

            elif data.startswith(b"receiver"):
                print("[%s %s] New Client is Receiver" % self.client_address)

                if serverInterface.is_empty():
                    print("[%s %s] There is no sender!" % self.client_address)
                    return
                else:
                    serverInterface.add_listener(self)

                    self.running = True

            else:
                print("[%s %s] Do not understand new Client!" % self.client_address)
                return

        else:
            print("[%s %s] New Client does not respond!" % self.client_address)
            return

        if serverInterface.is_sender(self):
            while self.running:
                buffer = self.recv_exact()
                if buffer:
                    serverInterface.add_buffer(buffer)

        else:
            while self.running:
                try:
                    buffer = serverInterface.get_buffer(self)
                    if buffer != 0:
                        self.request.sendall(buffer)
                except (ConnectionResetError, BrokenPipeError):
                    self.running = False
                    print("[%s %s] Removing Client" % self.client_address)
                    return


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("settings.conf")

    start_buffer_size = int(config["DEFAULT"]["BufferSize"])

    try:
        socketserver.ThreadingTCPServer(("", int(config["DEFAULT"]["Port"])), RequestHandler).serve_forever()
    except KeyboardInterrupt:
        pass

