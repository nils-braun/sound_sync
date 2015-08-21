from sound_sync.buffer_list import BufferList

class ClientBufferListHandler(BufferList):
    def __init__(self):
        self.current_buffer_index = -1
        BufferList.__init__(self)

    def add_buffer_with_index(self, sound_buffer, buffer_index):
        if buffer_index == self.end_buffer_index + 1:
            self.add_buffer(sound_buffer)
        else:
            raise IndexError

    def get_current_playable_buffer(self):
        if self.current_buffer_index > self.end_buffer_index:
            raise IndexError
        self.current_buffer_index += 1
        return self.get_buffer_by_buffer_index(self.current_buffer_index - 1)