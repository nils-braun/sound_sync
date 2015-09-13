from collections import deque


class SoundBufferList:
    def __init__(self, max_length):
        self.deque = deque(maxlen=max_length)

    def add_buffer(self, buffer):
        self.deque.append((self.next_free_index, buffer))

    def get_buffer(self, buffer_number):
        if self.next_free_index > buffer_number >= self.start_index:
            return self.deque[buffer_number - self.start_index][1]
        else:
            raise KeyError

    @property
    def start_index(self):
        if len(self.deque) > 0:
            start_index, start_buffer = self.deque[0]
            return start_index
        else:
            return 0

    @property
    def next_free_index(self):
        return self.start_index + len(self.deque)