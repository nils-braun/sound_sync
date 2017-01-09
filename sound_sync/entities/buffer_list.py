from collections import deque


class BufferList:
    def __init__(self, max_buffer_size):
        self.start_index = 0
        self.max_buffer_size = max_buffer_size

        self.buffers = deque(maxlen=max_buffer_size)