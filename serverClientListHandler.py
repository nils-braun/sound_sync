import time

__author__ = 'nils'


class ClientListHandler:
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
        Remove the listener from the list and delete the period number in the period number list.
        """
        self.listener_buffer_number.pop(self.listener.index(listener))
        self.listener.remove(listener)