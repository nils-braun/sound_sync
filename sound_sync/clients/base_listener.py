from sound_sync.clients.connection import SoundSyncConnection
from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Client, Channel
from sound_sync.timing.timer import Timer


class BaseListener(Client):
    def __init__(self, channel_hash=None, host=None, manager_port=None):
        Client.__init__(self)

        #: The connection to the rest server
        self.connection = SoundSyncConnection(host, manager_port)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The channel we are listening to
        self._connected_channel = None

        #: The player to send the data to
        self.player = None

        #: The threads to handle the playing
        self.play_threads = None

        #: The currently last played buffer number
        self.next_expected_buffer_number = None

    def initialize(self):
        if self.client_hash is not None:
            return

        if self.channel_hash is None:
            raise ValueError()

        self.client_hash = self.connection.add_client_to_server()
        self.get_settings()
        self.connection.set_name_of_client(self.name, self.client_hash)

        self.player.initialize()

    @property
    def handler_string(self):
        if self._connected_channel is None or self._connected_channel.handler_port is None:
            raise ValueError()

        return "http://" + str(self.connection.host) + ":" + str(self._connected_channel.handler_port)

    def terminate(self):
        if self.client_hash is None:
            return

        self.connection.remove_client_from_server(self.client_hash)
        self.client_hash = None

        self.player.terminate()

    def get_settings(self):
        if self.channel_hash is None:
            raise ValueError()

        channel_information = self.connection.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def main_loop(self):
        if self.client_hash is None:
            raise AssertionError("Listener needs to be initialized first")

        self.next_expected_buffer_number = self.get_current_buffer_start_index()

        # Receive information from the buffer server if possible
        while True:
            current_end_index = self.get_current_buffer_end_index()
            if current_end_index >= self.next_expected_buffer_number:
                self.receive_and_play_next_buffer()

    def receive_and_play_next_buffer(self):
        temp_buffer = self.get_buffer(self.next_expected_buffer_number)
        temp_extracted_buffer = SoundBufferWithTime.construct_from_string(temp_buffer)
        assert temp_extracted_buffer.buffer_number == self.next_expected_buffer_number

        self.play_buffer(temp_extracted_buffer)
        self.next_expected_buffer_number += 1

    def get_buffer_index(self, type):
        response = self.connection.http_client.fetch(self.handler_string + "/" + type)
        return int(response.body)

    def get_current_buffer_start_index(self):
        return self.get_buffer_index("start")

    def get_current_buffer_end_index(self):
        return self.get_buffer_index("end")

    def get_buffer(self, buffer_number):
        response = self.connection.http_client.fetch(self.handler_string + "/get/%d" % buffer_number, raise_error=False)
        if response.code == 200:
            return response.body
        else:
            raise RuntimeError(response)

    def play_buffer(self, sound_buffer_with_time):
        def play():
            self.player.put(sound_buffer_with_time.sound_buffer)

        timer = Timer(sound_buffer_with_time.buffer_time, play)
        timer.start()
