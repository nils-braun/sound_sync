from sound_sync.audio.mock.device import MockDevice
from sound_sync.timing.time_utils import sleep


class MockRecorder(MockDevice):
    def __init__(self):
        super().__init__()

        self.buffer_number = 0

    def get(self):
        current_sound_buffer = str(self.buffer_number).encode()

        current_length = len(current_sound_buffer)

        self.buffer_number += 1

        sleep(self.get_waiting_time().microseconds * 1e-6)

        return current_sound_buffer, current_length
