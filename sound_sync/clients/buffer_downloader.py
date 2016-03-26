from sound_sync.timing.time_utils import sleep

try:
    from sound_sync.buffer_server import BufferList
except ImportError:
    from buffer_server import BufferList

from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime


class BufferDownloader():
    def __init__(self, fetch_method, buffer_list):
        #: The connection used for getting the buffer
        self.fetch_method = fetch_method

        #: The handler url to connect to. Is set in the initialize method.
        self.handler_string = None

        self.buffer_list = buffer_list

    def initialize(self, handler_string):
        self.handler_string = handler_string

    def get_buffer_index(self, type):
        response = self.fetch_method(self.handler_string + "/" + type)
        return int(response.body)

    def get_current_buffer_start_index(self):
        return self.get_buffer_index("start")

    def get_current_buffer_end_index(self):
        return self.get_buffer_index("end")

    def get_buffer(self, buffer_number):
        response = self.fetch_method(self.handler_string + "/get/%d" % buffer_number, raise_error=False)
        if response.code == 200:
            return response.body
        else:
            raise RuntimeError(response)

    def main_loop(self):
        if not self.handler_string:
            raise ValueError()

        next_expected_buffer_number = self.get_current_buffer_start_index()
        self.buffer_list.set_start_index(next_expected_buffer_number)

        while True:
            current_end_index_server = self.get_current_buffer_end_index()
            current_end_index_local = self.buffer_list.get_next_free_index() - 1

            if current_end_index_server > current_end_index_local:
                next_buffer_index = current_end_index_local + 1
                for i in xrange(100):
                    try:
                        temp_buffer = self.get_buffer(next_buffer_index)
                        break
                    except RuntimeError:
                        pass

                temp_extracted_buffer = SoundBufferWithTime.construct_from_string(temp_buffer)
                assert temp_extracted_buffer.buffer_number == next_buffer_index

                self.buffer_list.add_buffer(temp_buffer)
            else:
                sleep(0.2)