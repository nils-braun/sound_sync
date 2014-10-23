#!/usr/bin/env python
"""
This module implements the server.
"""
import time
from socket import error as SocketError

from serverBase import ServerBase
from serverClientListHandler import ClientListHandler, IndexToHighException, IndexToLowException, EmptyException

import SocketServer

PORT = 50007                # TODO: Should better be read from a file...

__author__ = "nilpferd1991"
__version__ = "2.0.0"


class RequestHandler(SocketServer.BaseRequestHandler, ServerBase):
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

        ServerBase.__init__(self)
        self.client = request
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        self.handle_new_client()
        self.mainloop()

    def mainloop(self):
        if RequestHandler.static_client_list.is_sender(self):
            while self.running:
                self.mainloop_sender()

            self.client.close()
        else:
            while self.running:
                self.mainloop_listener()

            self.client.close()

    def handle_new_client(self):
        print("[%s %s] Added new Client." % self.client_address)
        first_identity_message = self.receive()
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
        self.send_ok()
        self.receive_ok()

        if RequestHandler.static_client_list.no_sender():
            # Kill the client if we have no sender.
            # TODO Better Error Handling!
            print("[%s %s] There is no sender!" % self.client_address)
            self.running = False
        else:
            self.send_information(RequestHandler.clientInformation.frame_rate)
            self.send_information(RequestHandler.clientInformation.waiting_time)
            self.send_information(RequestHandler.static_client_list.start_time)

            RequestHandler.static_client_list.add_listener(self)

            self.running = True
            print("[%s %s] Added new Listener." % self.client_address)

    def handle_new_sender(self):
        print("[%s %s] New Client is Sender." % self.client_address)
        self.send_ok()

        RequestHandler.clientInformation.frame_rate = int(self.receive_information())
        RequestHandler.clientInformation.waiting_time = int(self.receive_information())
        RequestHandler.clientInformation.set_sound_buffer_size()

        RequestHandler.static_client_list.add_sender(self)

        self.running = True
        print("[%s %s] Added new Sender." % self.client_address)

    def handle_new_unknown(self):
        # The new client is neither sender nor listener. Kill it.
        print("[%s %s] Do not understand new Client or is not responding!" % self.client_address)
        self.running = False

    def mainloop_sender(self):
        try:
            new_sound_buffer = self.receive_buffer_with_exact_length()
            if new_sound_buffer:
                RequestHandler.static_client_list.add_buffer(new_sound_buffer)
            else:
                self.remove_sender()
        except SocketError:
            self.remove_sender()

    def mainloop_listener(self):
        # A running listener waits for a message with to parts: First the current period number to calibrate
        # its own buffers list, than the buffer itself. We try to send it to him except the case
        # the listener is not there anymore. Then we release it and remove it from the serverInterface.

        if RequestHandler.static_client_list.is_empty():
            print("[%s %s] There are no buffers!" % self.client_address)
            self.remove_listener()
            return

        try:
            buffer_index = RequestHandler.static_client_list.get_buffer_index(self)
            self.send_information(buffer_index)
            self.send(RequestHandler.static_client_list.get_buffer(self))

        except SocketError:
            self.remove_listener()
        except IndexToHighException:
            # Sleeping 1 ms is better for performance issues (??)
            time.sleep(1 / 1000.0)

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
    server = SocketServer.ThreadingTCPServer(("", ServerBase.addressInformation.port), RequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    main()

