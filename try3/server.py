#!/usr/bin/env python3

# TODO: comments!

import socketserver
import time
from socket import error as SocketError

start_buffer_size = 1024
buffer_size = 0


class ServerInterface:
    def __init__(self):
        self.sender = 0
        self.listener = list()
        self.listener_buffer_number = list()
        self.buffers = list()
        self.start_pointer = 0
        self.start_time = 0
        self.end_pointer = 0
        self.buffer_size = 10
        self.client_waiting_time = 0
        self.client_frame_rate = 0

    def add_sender(self, sender):
        self.sender = sender

    def add_listener(self, listener):
        self.listener.append(listener)
        if len(self.listener_buffer_number) > 0:
            self.listener_buffer_number.append(max(self.listener_buffer_number))
        else:
            self.listener_buffer_number.append(self.start_pointer)

    def add_buffer(self, buffer):
        self.buffers.append(buffer)
        if self.end_pointer == 0:
            # first buffer
            self.start_time = time.time()
        self.end_pointer += 1
        if len(self.buffers) > self.buffer_size:
            self.buffers.pop(0)
            self.start_pointer += 1

    def get_index(self, listener):
        index = self.listener_buffer_number[self.listener.index(listener)]
        if index < self.start_pointer:
            self.listener_buffer_number[self.listener.index(listener)] = self.start_pointer + 1
            return self.start_pointer + 1
        elif index >= self.end_pointer:
            return False
        else:
            return index

    def get_buffer(self, listener):
        if self.get_index(listener):
            buffer = self.buffers[self.get_index(listener) - self.start_pointer]
            self.listener_buffer_number[self.listener.index(listener)] += 1
            return buffer
        else:
            return 0

    def is_sender(self, sender):
        return self.sender is sender

    def is_empty(self):
        return self.end_pointer == 0

    def no_sender(self):
        return self.sender == 0

    def remove_sender(self):
        self.sender = 0

    def remove_listener(self, listener):
        self.listener_buffer_number.pop(self.listener.index(listener))
        self.listener.remove(listener)

serverInterface = ServerInterface()


# Listen on a port
# If a client starts sending packages, echo them to all other clients
class RequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):

        self.running = False

        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def recv_exact(self):
        pointer = 0
        tmp_buffer = bytearray(buffer_size)
        while pointer < buffer_size:
            data = self.request.recv(buffer_size - pointer)
            if not data:
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    # this function is called everytime a new client wants to get access to the server
    def handle(self):

        global buffer_size

        print("[%s %s] Added new Client." % self.client_address)

        # Receive first message to switch between sender and listener
        data = self.request.recv(start_buffer_size)

        if data:
            if data.startswith(b"sender"):
                print("[%s %s] New Client is Sender." % self.client_address)
                self.request.sendall(b"ok")

                # Receive frame rate in Hz
                serverInterface.client_frame_rate = int(self.request.recv(start_buffer_size))
                self.request.sendall(b"ok")

                # Receive waiting time in ms
                serverInterface.client_waiting_time = int(self.request.recv(start_buffer_size))
                self.request.sendall(b"ok")

                buffer_size = int(4*serverInterface.client_waiting_time / 1000.0 * serverInterface.client_frame_rate)

                serverInterface.add_sender(self)
                self.running = True
                print("[%s %s] Added new Sender." % self.client_address)

            elif data.startswith(b"receiver"):
                print("[%s %s] New Client is Receiver." % self.client_address)

                if serverInterface.no_sender():
                    print("[%s %s] There is no sender!" % self.client_address)
                    return
                else:

                    self.request.sendall(str(serverInterface.client_frame_rate).encode())
                    self.request.recv(start_buffer_size)

                    self.request.sendall(str(serverInterface.client_waiting_time).encode())
                    self.request.recv(start_buffer_size)

                    self.request.sendall(str(serverInterface.start_time).encode())
                    self.request.recv(start_buffer_size)

                    serverInterface.add_listener(self)
                    self.running = True
                    print("[%s %s] Added new Listener." % self.client_address)

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
                    print("[%s %s] Removing Client" % self.client_address)
                    serverInterface.remove_sender()
                    self.running = False
                    return

        else:
            while self.running:
                try:
                    if serverInterface.is_empty():
                        print("[%s %s] There is no sender!" % self.client_address)
                        return

                    index = serverInterface.get_index(self)
                    if index:
                        self.request.sendall(str(index).encode())
                        self.request.recv(start_buffer_size)
                        self.request.sendall(serverInterface.get_buffer(self))

                    # Is sleeping 1 ms better for performance issues?
                    time.sleep(1/1000.0)
                except SocketError:
                    print("[%s %s] Removing Client" % self.client_address)
                    serverInterface.remove_listener(self)
                    self.running = False
                    return


if __name__ == "__main__":

    server = socketserver.ThreadingTCPServer(("", 50007), RequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

