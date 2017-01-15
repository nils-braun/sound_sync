import json
from threading import Thread

from sound_sync.clients.connection import Subscriber
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.entities.channel import Channel
from sound_sync.entities.json_pickable import JSONPickleable


class DownloaderThread(Thread):
    def __init__(self, parent, host, port, channel_hash):
        super().__init__()

        #: The connection to the rest server
        self.connection = Subscriber(host, port, channel_hash)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The channel we are listening to
        self._connected_channel = None

        #: The calling parent class
        self.parent = parent

        #: Set to false, if the thread should be terminated
        self.should_run = True

    def use_settings(self, channel_information):
        JSONPickleable.fill_with_json(self.parent.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def stop(self):
        self.should_run = False

    def run(self):
        while self.should_run:
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
                #print("Got content", message)
                sound_buffer_with_time = SoundBufferWithTime.construct_from_string(str(message.message_body, encoding="utf8"))

                self.parent.buffer_list.append(sound_buffer_with_time)

            else:
                raise ValueError(message)