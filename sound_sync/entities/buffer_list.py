from collections import deque


class BufferList:
    def __init__(self, max_buffer_size):
        self.start_index = 0
        self.max_buffer_size = max_buffer_size

        self.buffers = deque(maxlen=max_buffer_size)

    def set_start_index(self, start_index):
        self.start_index = start_index

    def get_start_index(self):
        return self.start_index

    def get_next_free_index(self):
        return self.start_index + len(self.buffers)

    def add_buffer(self, buffer):
        if len(self.buffers) == self.max_buffer_size:
            self.start_index += 1
        self.buffers.append(buffer)

    def get_buffer(self, buffer_index):
        translated_buffer_index = int(buffer_index) - self.start_index
        if translated_buffer_index < 0 or translated_buffer_index >= len(self.buffers):
            raise RuntimeError("Wrong buffer index number")
        return self.buffers[translated_buffer_index]