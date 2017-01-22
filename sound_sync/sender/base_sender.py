from sound_sync.clients.connection import Publisher
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.entities.channel import Channel
from sound_sync.timing.time_utils import get_current_date


class BaseSender(Channel):
    def __init__(self, host, port, hash):
        Channel.__init__(self)

        #: The connection to the rest server
        self.connection = Publisher(host, port, hash)

        #: The recorder used for recording the sound data
        self.recorder = None

        self.channel_hash = hash

    def initialize(self):
        self.connection.add_channel_to_server()
        self.connection.set_name_and_description_of_channel(self.name, self.description)

        # TODO: Send sound settings

        self.recorder.initialize()

    def main_loop(self):
        starting_time = get_current_date()
        buffer_number = 0

        while True:
            sound_buffer, length = self.recorder.get()
            # TODO: Better use the real time here?
            buffer_time = starting_time + self.recorder.get_waiting_time() * buffer_number

            send_buffer = SoundBufferWithTime(sound_buffer=sound_buffer,
                                              buffer_number=buffer_number,
                                              buffer_time=buffer_time)

            self.connection.add_buffer(send_buffer)
            buffer_number += 1

    def terminate(self):
        self.connection.remove_channel_from_server()