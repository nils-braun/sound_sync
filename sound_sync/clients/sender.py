import urllib
import argparse

from tornado import httpclient

from sound_sync.audio.pcm.record import PCMRecorder
from sound_sync.clients.base import SoundSyncConnectedProgram
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Channel


class Sender(Channel, SoundSyncConnectedProgram):
    def __init__(self, host=None, manager_port=None):
        Channel.__init__(self)
        SoundSyncConnectedProgram.__init__(self, host, manager_port)

        #: The recorder used for recording the sound data
        self.recorder = PCMRecorder()

    def initialize(self):
        if self.channel_hash is not None:
            return

        self.channel_hash = self.add_channel_to_server()
        self.get_settings()
        self.set_name_and_description_of_channel(self.name, self.description, self.channel_hash)
        self.recorder.initialize()

    def main_loop(self):
        if self.channel_hash is None:
            raise AssertionError("Sender needs to be initialized first")

        while True:
            sound_buffer, length = self.recorder.get()
            parameters = {"buffer": sound_buffer}
            body = urllib.urlencode(parameters)
            self.http_client.fetch(self.handler_string + '/add',
                                   method="POST", body=body)

    def terminate(self):
        if self.channel_hash is None:
            return

        self.remove_channel_from_server(self.channel_hash)
        self.channel_hash = None

    def get_settings(self):
        channel_information = self.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.recorder, channel_information)
        self.handler_port = channel_information["handler_port"]

    @property
    def handler_string(self):
        if self.handler_port is None:
            raise ValueError()

        return "http://" + str(self.host) + ":" + str(self.handler_port)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--hostname",
                        default="localhost",
                        type=str,
                        help="Hostname of the management server.",
                        dest="hostname")
    parser.add_argument("-p", "--port",
                        default=8888,
                        type=int,
                        help="Port of the management socket on the management server. Default 8888.",
                        dest="manager_port")
    parser.add_argument("-n", "--name",
                        default="Untitled",
                        type=str,
                        help="Name of this channel in the channel list. Default Untitled.",
                        dest="name")
    parser.add_argument("-d", "--description",
                        default="No Description",
                        type=str,
                        help="Description of this channel in the channel list. Default No Description.",
                        dest="description")
    args = parser.parse_args()
    sender = Sender(args.host, args.manager_port)
    sender.name = args.name
    sender.description = args.description
    sender.initialize()
    try:
        sender.main_loop()
    finally:
        sender.terminate()


if __name__ == "__main__":
    main()