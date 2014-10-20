#!/usr/bin/env python
"""
This module implements the server.
"""
import time
from socket import error as SocketError

from serverBase import ServerBase
from serverClientListHandler import ClientListHandler

import SocketServer as socketserver

PORT = 50007                # TODO: Should better be read from a file...

__author__ = "nilpferd1991"
__version__ = "2.0.0"


class RequestHandler(socketserver.BaseRequestHandler, ServerBase):
    """
    This class is the RequestHandler of the server. It collects data from the new clients (if it is a sender or a
    listener) and receives buffers from senders or sends buffers to listeners. It is threaded - so every new client
    is a new thread.

    First, the server listens to port 50007 for new clients. Then it asks for sender or listener.

    Senders send the frame_rate and the waiting_time to the server. Then they start sending audio buffers which
    are moved into the buffers list of the serverInterface to store them. The index handling is implemented there.

    Listeners receive the frame_rate, the waiting_time and the start_time when the first audio buffer of the sender
    was pushed to the server. Then a listener pulls for new data which we send to this client, if its period number
    is not to far away in the future.
    """

    static_client_list = ClientListHandler()

    def __init__(self, request, client_address, server):
        self.running = False            # set to False to stop the server

        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        ServerBase.__init__(self, self.request)

    def handle(self):
        """
        This function is called every time a new client wants to get access to the server. It tries to get the type of
        the new client and handles the messaging as describes above.
        """

        self.handle_new_client()
        self.mainloop()

    def mainloop(self):
        if RequestHandler.static_client_list.is_sender(self):
            while self.running:
                self.mainloop_sender()
        else:
            while self.running:
                self.mainloop_listener()

    def handle_new_client(self):
        print("[%s %s] Added new Client." % self.client_address)
        first_identity_message = self.receive_message()
        if first_identity_message:
            if first_identity_message.startswith(b"sender"):
                self.handle_new_sender()
            elif first_identity_message.startswith(b"receiver"):
                self.handle_new_listener()
            else:
                self.handle_new_unknown()
        else:
            self.handle_new_unknown()

    def handle_new_listener(self):
        print("[%s %s] New Client is Listener." % self.client_address)
        self.say_ok()

        if RequestHandler.static_client_list.no_sender():
            # Kill the client if we have no sender.
            # TODO Better Error Handling!
            print("[%s %s] There is no sender!" % self.client_address)
            self.running = False
        else:
            self.send_information(RequestHandler.static_client_list.client_frame_rate)
            self.send_information(RequestHandler.static_client_list.client_waiting_time)
            self.send_information(RequestHandler.static_client_list.start_time)

            RequestHandler.static_client_list.add_listener(self)

            self.running = True
            print("[%s %s] Added new Listener." % self.client_address)

    def handle_new_sender(self):
        print("[%s %s] New Client is Sender." % self.client_address)
        self.say_ok()

        RequestHandler.static_client_list.client_frame_rate = int(self.receive_information())
        RequestHandler.static_client_list.client_waiting_time = int(self.receive_information())
        self.set_buffer_size(RequestHandler.static_client_list.client_waiting_time,
                             RequestHandler.static_client_list.client_frame_rate)

        RequestHandler.static_client_list.add_sender(self)

        self.running = True
        print("[%s %s] Added new Sender." % self.client_address)

    def handle_new_unknown(self):
        # The new client is neither sender nor listener. Kill it.
        print("[%s %s] Do not understand new Client or is not responding!" % self.client_address)
        self.running = False

    def mainloop_sender(self):
        # If the client is a sender and the status is set to running, we receive a new buffer
        # of the exact size of self.buffer_length and add it to the buffers list.
        # If the sender stops sending data, we release it and remove it from the serverInterface.
        new_sound_buffer = self.receive_exact()
        if new_sound_buffer:
            RequestHandler.static_client_list.add_buffer(new_sound_buffer)
        else:
            self.remove_sender()

    def mainloop_listener(self):
        # A running listener waits for a message with to parts: First the current period number to calibrate
        # its own buffers list, than the buffer itself. We try to send it to him except the case
        # the listener is not there anymore. Then we release it and remove it from the serverInterface.
        try:
            # Do not send data if there is no client.
            if RequestHandler.static_client_list.is_empty():
                print("[%s %s] There is no sender!" % self.client_address)
                self.remove_listener()

            # Send the period number and the buffer to the listener if it is not to far ahead.
            else:
                buffer_index = RequestHandler.static_client_list.get_index(self)
                if buffer_index:
                    self.send_information(buffer_index)
                    self.send_message(RequestHandler.static_client_list.get_buffer(self))

            # Sleeping 1 ms is better for performance issues
            time.sleep(1 / 1000.0)
        except SocketError:
            self.remove_listener()

    def remove_sender(self):
        print("[%s %s] Removing Sender" % self.client_address)
        RequestHandler.static_client_list.remove_sender()
        self.running = False

    def remove_listener(self):
        print("[%s %s] Removing Listener" % self.client_address)
        RequestHandler.static_client_list.remove_listener(self)
        self.running = False


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

