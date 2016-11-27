from sound_sync.clients.threaded_sub_listener import ThreadedSubListener
from sound_sync.timing.time_utils import sleep
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime


class BufferDownloaderThread(ThreadedSubListener):
    def __init__(self, parent_listener):
        super(BufferDownloaderThread, self).__init__(parent_listener)

        self.maximum_retries = 100

    def get_buffer_index(self, start_or_end):
        assert(start_or_end in ["start", "end"])
        response = self.parent_listener.connection.http_client.fetch(self.parent_listener.handler_string + "/" + start_or_end)

        return int(response.body)

    def get_current_buffer_start_index(self):
        return self.get_buffer_index("start")

    def get_current_buffer_end_index(self):
        return self.get_buffer_index("end")

    def get_buffer(self, buffer_number):
        response = self.parent_listener.connection.http_client.fetch(self.parent_listener.handler_string + "/get/%d" % buffer_number,
                                                                     raise_error=False)
        if response.code == 200:
            return response.body
        else:
            print(response.body)
            raise RuntimeError(response)

    def run(self):
        if not self.parent_listener.handler_string:
            raise ValueError()

        next_expected_buffer_number = self.get_current_buffer_start_index()
        self.parent_listener.buffer_list.set_start_index(next_expected_buffer_number)

        while self._should_run:
            current_end_index_server = self.get_current_buffer_end_index() - 1
            current_end_index_local = self.parent_listener.buffer_list.get_next_free_index()

            if current_end_index_server > current_end_index_local:
                next_buffer_index = current_end_index_local + 1

                temp_buffer = None

                for i in range(self.maximum_retries):
                    try:
                        temp_buffer = self.get_buffer(next_buffer_index)
                        break
                    except RuntimeError:
                        pass

                if not temp_buffer:
                    raise RuntimeError

                temp_extracted_buffer = SoundBufferWithTime.construct_from_string(temp_buffer)
                assert temp_extracted_buffer.buffer_number == next_buffer_index

                print("Having", next_buffer_index)
                self.parent_listener.buffer_list.add_buffer(temp_buffer)
            else:
                sleep(0.2)