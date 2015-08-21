from collections import deque
from multiprocessing import Lock

__author__ = 'nils'


class BufferList:
    """
    Class for a typical ring buffer handling the sound buffer storage
    on the server or on the listener clients.
    """

    def __init__(self, max_buffer_length=50):
        """
        Initialize with the max_buffer_length size
        :param max_buffer_length int: The size of the buffer. If there are more elements
         than space, the oldest elements are deleted.
        """
        self.max_buffer_length = max_buffer_length
        self.buffers = deque()
        self.start_buffer_index = 0
        self.end_buffer_index = -1

    def add_buffer(self, sound_buffer):
        """
        Add a buffer to the list.
        :param sound_buffer T: The buffer to add
        :return: The number of the added buffer
        """
        mutex = Lock()
        mutex.acquire()
        self.buffers.append(sound_buffer)
        self.end_buffer_index += 1

        if len(self.buffers) > self.max_buffer_length:
            self.buffers.popleft()
            self.start_buffer_index += 1

        mutex.release()

        return self.start_buffer_index + len(self.buffers)

    def is_empty(self):
        """
        Check if the list is empty
        :return bool: if the list is empty
        """
        return len(self.buffers) == 0

    def get_buffer_by_buffer_index(self, index):
        """
        Return the buffer with the given index or raise an exception if it can not be found
        :param index int: the index of the buffer
        :return T: the sound buffer
        """

        list_index = index - self.start_buffer_index
        if list_index < 0 or list_index >= self.max_buffer_length:
            raise IndexError
        else:
            return self.buffers[list_index]