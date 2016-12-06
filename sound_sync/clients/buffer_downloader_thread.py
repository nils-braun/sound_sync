from sound_sync.clients.threaded_sub_listener import ThreadedSubListener
from sound_sync.timing.time_utils import sleep
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from tornado.httpclient import HTTPError


class BufferDownloaderThread(ThreadedSubListener):
    def __init__(self, parent_listener):
        super(BufferDownloaderThread, self).__init__(parent_listener)

        self.maximum_retries = 100

    def run(self, testing_mode=False):
        if not self.parent_listener.channel_hash:
            raise ValueError()

        channel_hash = self.parent_listener.channel_hash

        next_expected_buffer_number = self.parent_listener.connection.get_start_index(channel_hash) + 10
        self.parent_listener.buffer_list.set_start_index(next_expected_buffer_number)

        while self._should_run:
            current_end_index_server = self.parent_listener.connection.get_end_index(channel_hash)
            current_end_index_local = self.parent_listener.buffer_list.get_next_free_index()

            if current_end_index_server > current_end_index_local:
                next_buffer_index = current_end_index_local

                temp_buffer = None

                for i in range(self.maximum_retries):
                    try:
                        temp_buffer = self.parent_listener.connection.get_buffer_raw(next_buffer_index, channel_hash)
                        break
                    except HTTPError:
                        pass

                if not temp_buffer:
                    raise RuntimeError

                temp_extracted_buffer = SoundBufferWithTime.construct_from_string(temp_buffer)
                assert temp_extracted_buffer.buffer_number == next_buffer_index

                print("Having", next_buffer_index)
                self.parent_listener.buffer_list.add_buffer(temp_buffer)
            elif testing_mode:
                return
            else:
                sleep(0.2)
