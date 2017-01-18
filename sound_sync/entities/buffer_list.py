from collections import deque


class RingBufferList:
    def __init__(self, max_buffer_size):
        self.buffers = deque(maxlen=max_buffer_size)

    def __getitem__(self, item):
        return self.buffers[item]

    def append(self, message):
        self.buffers.append(message)


class OrderedBufferList:
    def __init__(self, max_buffer_size):
        self._buffers = deque(maxlen=max_buffer_size)

        for i in range(max_buffer_size):
            self._buffers.append(None)

        self._start_index = None

    def append(self, item):
        item_buffer_number = item.buffer_number

        if self._start_index is None:
            self._start_index = item_buffer_number

        index_number = item_buffer_number - self._start_index
        if index_number >= 0:
            self._buffers[index_number] = item

    def pop(self):
        return_buffer = self._buffers.popleft()

        self._start_index += 1

        assert self._buffers[0] is None or self._buffers[0].buffer_number == self._start_index

        # Always keep the buffer full
        self._buffers.append(None)

        if return_buffer:
            return return_buffer
        else:
            raise IndexError

    def is_continuous_until(self, n):
        if n >= len(self._buffers):
            return False
        return all([self._buffers[i] for i in range(n + 1)])