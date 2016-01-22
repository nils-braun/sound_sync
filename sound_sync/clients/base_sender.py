import urllib

from sound_sync.clients.connection import SoundSyncConnection
from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Channel
from sound_sync.timing.time_utils import get_current_date


class BaseSender(Channel):
    def __init__(self, host=None, manager_port=None):
        Channel.__init__(self)

        #: The connection to the rest server
        self.connection = SoundSyncConnection(host, manager_port)

        #: The recorder used for recording the sound data
        self.recorder = None

    def initialize(self):
        if self.channel_hash is not None:
            return

        self.channel_hash = self.connection.add_channel_to_server()
        self.get_settings()
        self.connection.set_name_and_description_of_channel(self.name, self.description, self.channel_hash)

        self.recorder.initialize()

    def main_loop(self):
        if self.channel_hash is None:
            raise AssertionError("Sender needs to be initialized first")

        starting_time = get_current_date()
        buffer_number = 0

        while True:
            sound_buffer, length = self.recorder.get()
            buffer_time = starting_time + self.recorder.get_waiting_time() * buffer_number

            send_buffer = SoundBufferWithTime(sound_buffer=sound_buffer,
                                              buffer_number=buffer_number,
                                              buffer_time=buffer_time)

            parameters = {"buffer": send_buffer.to_string()}
            body = urllib.urlencode(parameters)
            self.connection.http_client.fetch(self.handler_string + '/add',
                                              method="POST", body=body)
            buffer_number += 1

    def terminate(self):
        if self.channel_hash is None:
            return

        self.connection.remove_channel_from_server(self.channel_hash)
        self.channel_hash = None

    def get_settings(self):
        channel_information = self.connection.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.recorder, channel_information)
        self.handler_port = channel_information["handler_port"]

    @property
    def handler_string(self):
        if self.handler_port is None:
            raise ValueError()

        return "http://" + str(self.connection.host) + ":" + str(self.handler_port)
