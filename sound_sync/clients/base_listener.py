import json
from datetime import timedelta

from sound_sync.clients.connection import Subscriber
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.entities.channel import Channel
from sound_sync.entities.json_pickable import JSONPickleable
from sound_sync.timing.timer import Timer


class BaseListener:
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

            if message.message_type == b"control":
                print("Got control message", message)
            elif message.message_type == b"parameters":
                print("Got settings", message)
                if self._connected_channel is None:
                    parameters = json.loads(str(message.message_body, encoding="utf8"))
                    self.use_settings(parameters)
                else:
                    print("Not implemented in the moment")
            elif message.message_type == b"content":
                print("Got content", message)

                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(str(message.message_body, encoding="utf8"))

                def play():
                    print("Playing", sound_buffer_with_time.buffer_number)
                    self.player.put(sound_buffer_with_time.sound_buffer)

                sound_buffer_with_time.buffer_time += timedelta(seconds=10)
                print("Starting player for", sound_buffer_with_time.buffer_number,
                      "at", sound_buffer_with_time.buffer_time)

                try:
                    timer = Timer(sound_buffer_with_time.buffer_time, play)
                    timer.start()
                except ValueError:
                    print("Value error")
                    pass
            else:
                raise ValueError(message)