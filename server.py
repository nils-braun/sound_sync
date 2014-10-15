#!/usr/bin/env python
"""
This module implements the server.
"""

START_BUFFER_SIZE = 1024
PORT = 50007                # TODO: Should better be read from a file...

__author__ = "nilpferd1991"
__version__ = "2.0.0"

import SocketServer as socketserver
import time
from socket import error as SocketError


class ServerInterface:
    """
    This class implements the message buffer und the saving of the parameters for the various senders and listeners.
    """
    def __init__(self):
        self.sender = 0                         # the pointer to the sender
        self.listener = list()                  # the list of current listeners
        self.listener_buffer_number = list()    # the list of the period number of the current listeners.
        self.buffers = list()                   # the list with the current buffers from the sender
        self.start_pointer = 0                  # the index of the first buffer in the buffers list
        self.start_time = 0                     # the time when the client started sending data. Should be send to the
                                                # listeners with the information of the current period number for them to
                                                # calibrate their buffer list
        self.end_pointer = 0                    # the index of the last item in the buffers list
        self.buffer_size = 10                   # the maximum of numbers in the buffers list (arbitrary)
        self.client_waiting_time = 0            # the waiting time of the clients. Is received from the sender and
                                                # send to the listeners.
        self.client_frame_rate = 0              # Same procedure as the waiting time.

    def add_sender(self, sender):
        """
        Add a new sender and delete the information of the old sender. If there are listeners
        around, they should be killed!
        """
        self.sender = sender
        if len(self.listener) > 0:
            print("TODO: We have listeners here, but a new client! Aborting.")
            exit()
        self.listener = list()
        self.listener_buffer_number = list()
        self.buffers = list()
        self.start_pointer = 0
        self.start_time = 0
        self.end_pointer = 0

    def add_listener(self, listener):
        """
        Add a new listener. Set the current period number of this new listener to the highest period number
        of the other listeners or to the first buffer in the buffers list, if there are no other listeners.
        """
        self.listener.append(listener)
        if len(self.listener_buffer_number) > 0:
            self.listener_buffer_number.append(max(self.listener_buffer_number))
        else:
            self.listener_buffer_number.append(self.start_pointer)

    def add_buffer(self, buffer):
        """
        Add a new buffer to the buffers list coming from the client. Increase end_pointer and start_pointer
        accordingly. Sets the start_time if this buffer is the first one.
        """
        self.buffers.append(buffer)
        if self.end_pointer == 0:
            # first buffer
            self.start_time = time.time()
        self.end_pointer += 1
        if len(self.buffers) > self.buffer_size:
            # start deleting buffers if the buffers list is full
            self.buffers.pop(0)
            self.start_pointer += 1

    def get_index(self, listener):
        """
        Get the current period number of the listener. If the listener is fallen behind the beginning of the buffers
        list set the pointer to the start_pointer + 1. If the period number is ahead of the end of the buffers
        return False.
        """
        index = self.listener_buffer_number[self.listener.index(listener)]
        if index < self.start_pointer:
            self.listener_buffer_number[self.listener.index(listener)] = self.start_pointer + 1
            return self.start_pointer + 1
        elif index >= self.end_pointer:
            return False
        else:
            return index

    def get_buffer(self, listener):
        """
        Return the buffer the listener should receive next and increase the period number of this listener. If there is
        no new buffer (because the client is to far ahead), return 0.
        """
        if self.get_index(listener):
            buffer = self.buffers[self.get_index(listener) - self.start_pointer]
            self.listener_buffer_number[self.listener.index(listener)] += 1
            return buffer
        else:
            return 0

    def is_sender(self, sender):
        """
        Check if this client is the current sender.
        """
        return self.sender is sender

    def is_empty(self):
        """
        Check if we have started new recently.
        """
        return self.end_pointer == 0

    def no_sender(self):
        """
        Check if there is no sender pushing data to the server.
        """
        return self.sender == 0

    def remove_sender(self):
        """
        Remove the sender. A new sender should set all parameters new!
        """
        self.sender = 0

    def remove_listener(self, listener):
        """
        Remove the listener from teh list and delete the period number in the period number list.
        """
        self.listener_buffer_number.pop(self.listener.index(listener))
        self.listener.remove(listener)

# The static object to handle all parameters.
serverInterface = ServerInterface()


class RequestHandler(socketserver.BaseRequestHandler):
    """
    This class is the RequestHandler of the server. It collects data from the new clients (if it is a sender or a
    listener) and receives buffers from senders or sends buffers to listeners. It is threaded - so every new client
    is a new thread.

    First, the server listens to port 50007 for new clients. Then it asks for sender or receiver.

    Senders send the frame_rate and the waiting_time to the server. Then they start sending audio buffers which
    are moved into the buffers list of the serverInterface to store them. The index handling is implemented there.

    Listeners receive the frame_rate, the waiting_time and the start_time when the first audio buffer of the sender
    was pushed to the server. Then a listener pulls for new data which we send to this client, if its period number
    is not to far away in the future.
    """

    def __init__(self, request, client_address, server):

        self.running = False            # set to False to stop the server
        self.buffer_size = 0            # the buffer size of the clients is calculated from teh waiting_time and
                                        # the frame rate. Fo more information see ClientBase.
        self.start_buffer_size = START_BUFFER_SIZE   # The buffer_size to be used for pre-audio messaging.

        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)

    def recv_exact(self):
        """
        Receive exact buffer_size bytes from the client. If received less, repeat until the buffer
        is full. If an error occurred, return nothing.

        :rtype: bytearray, None
        """
        pointer = 0
        tmp_buffer = bytearray(self.buffer_size)
        while pointer < self.buffer_size:
            data = self.request.recv(self.buffer_size - pointer)
            if not data:
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def handle(self):
        """
        This function is called every time a new client wants to get access to the server. It tries to get the type of
        the new client and handles the messaging as describes above.
        """

        print("[%s %s] Added new Client." % self.client_address)

        # Receive first message to switch between sender and listener
        data = self.request.recv(self.start_buffer_size)

        if data:
            if data.startswith(b"sender"):
                # The sender sends frame_rate and waiting_time, which we store in the serverInterface.
                # We calculate the correct buffer_size (with factor 4!), save the client as
                # the new sender and set the status to running.
                print("[%s %s] New Client is Sender." % self.client_address)
                self.request.sendall(b"ok")

                # Receive frame rate in Hz
                serverInterface.client_frame_rate = int(self.request.recv(self.start_buffer_size))
                self.request.sendall(b"ok")

                # Receive waiting time in ms
                serverInterface.client_waiting_time = int(self.request.recv(self.start_buffer_size))
                self.request.sendall(b"ok")

                # Calculate the buffer size with factor 4!
                self.buffer_size = int(4*serverInterface.client_waiting_time / 1000.0 * serverInterface.client_frame_rate)

                # Add the sender to the serverInterface
                serverInterface.add_sender(self)

                # Set the status to running.
                self.running = True
                print("[%s %s] Added new Sender." % self.client_address)

            elif data.startswith(b"receiver"):
                # The listener receives the frame_rate, the waiting_time and the start_time if there is a client around.
                # Then is is added do the serverInterface and the status is set to running.
                print("[%s %s] New Client is Receiver." % self.client_address)

                if serverInterface.no_sender():
                    # Kill the client if we have no sender.
                    print("[%s %s] There is no sender!" % self.client_address)
                    return
                else:

                    # Send the frame_rate to the listener.
                    self.request.sendall(str(serverInterface.client_frame_rate).encode())
                    self.request.recv(self.start_buffer_size)

                    # Send the waiting_time to the listener.
                    self.request.sendall(str(serverInterface.client_waiting_time).encode())
                    self.request.recv(self.start_buffer_size)

                    # Send the start_time to the listener.
                    self.request.sendall(str(serverInterface.start_time).encode())
                    self.request.recv(self.start_buffer_size)

                    # Add the listener to the serverInterface.
                    serverInterface.add_listener(self)

                    # Set the status to running.
                    self.running = True
                    print("[%s %s] Added new Listener." % self.client_address)

            else:
                # The new client is neither sender nor listener. Kill it.
                print("[%s %s] Do not understand new Client!" % self.client_address)
                return

        else:
            # No initial message from the client. Kill it.
            print("[%s %s] New Client does not respond!" % self.client_address)
            return

        # Now the pre-audio messaging is done and we go on with sending audio buffers. We must handle senders and
        # listeners with the same method, so we use if:
        if serverInterface.is_sender(self):
            while self.running:
                # If the client is a sender and the status is set to running, we receive a new buffer
                # of the exact size of self.buffer_length and add it to the buffers list.
                # If the sender stops sending data, we release it and remove it from the serverInterface.
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
                # A running listener waits for a message with to parts: First the current period number to calibrate
                # its own buffers list, than the buffer itself. We try to send it to him except the case
                # the listener is not there anymore. Then we release it and remove it from the serverInterface.
                try:
                    # Do not send data if there is no client.
                    if serverInterface.is_empty():
                        print("[%s %s] There is no sender!" % self.client_address)
                        print("[%s %s] Removing Client" % self.client_address)
                        serverInterface.remove_listener(self)
                        self.running = False
                        return

                    # Send the period number and the buffer to the listener if it is not to far ahead.
                    index = serverInterface.get_index(self)
                    if index:
                        self.request.sendall(str(index).encode())
                        self.request.recv(self.start_buffer_size)
                        self.request.sendall(serverInterface.get_buffer(self))

                    # Sleeping 1 ms is better for performance issues
                    time.sleep(1/1000.0)
                except SocketError:
                    print("[%s %s] Removing Client" % self.client_address)
                    serverInterface.remove_listener(self)
                    self.running = False
                    return


def main():
    """
    The main function. Starts the TCP Server on port 50007 and receives new senders or listeners.
    """
    server = socketserver.ThreadingTCPServer(("", PORT), RequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    main()

