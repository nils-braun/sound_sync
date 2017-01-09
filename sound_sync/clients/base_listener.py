import json
from datetime import timedelta

from sound_sync.clients.connection import Subscriber
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Channel
from sound_sync.timing.timer import Timer


class BaseListener():
    def __init__(self, host, port, channel_hash):
        #: The connection to the rest server
        self.connection = Subscriber(host, port, channel_hash)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The channel we are listening to
        self._connected_channel = None

        #: The player to send the data to
        self.player = None

    def initialize(self):
        self.player.initialize()

    def terminate(self):
        self.player.terminate()

    def use_settings(self, channel_information):
        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def main_loop(self):
        while True:
            message = self.connection.receive()

            if message.message_type == "control":
                print("Got control message", message)
                break
            elif message.message_type == "parameters":
                print("Got settings", message)
                if self._connected_channel is None:
                    parameters = json.loads(str(message.message_body, encoding="utf8"))
                    self.use_settings(parameters)
                else:
                    raise RuntimeError()
            elif message.message_type == "content":
                print("Got content", message)

                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(message.message_type)

                def play():
                    print("Playing", sound_buffer_with_time.buffer_number)
                    self.player.put(sound_buffer_with_time.sound_buffer)

                sound_buffer_with_time.buffer_time += timedelta(seconds=23)
                print("Starting player for", sound_buffer_with_time.buffer_number,
                      "at", sound_buffer_with_time.buffer_time)

                try:
                    timer = Timer(sound_buffer_with_time.buffer_time, play)
                    timer.run()
                except ValueError:
                    print("Value error")
                    pass