import urllib
import argparse
import json

from tornado import httpclient

from sound_sync.clients.base import SoundSyncConnectedProgram
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.rest_server.server_items.server_items import Client


class Listener(Client, SoundSyncConnectedProgram):
    def __init__(self, channel_hash=None, host=None, manager_port=None):
        Client.__init__(self)
        SoundSyncConnectedProgram.__init__(host, manager_port)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The recorder used for recording the sound data
        self.player = PCMPlay()

        #: The channel we are listening to
        self._connected_channel = None

    def initialize(self):
        if self.client_hash is not None:
            return

        http_client = httpclient.HTTPClient()

        self.add_client_to_server(http_client)
        self.get_channel_from_server(http_client)
        self.get_settings(http_client)
        self.set_name_and_description_of_channel(http_client)
        self.player.initialize()

    @property
    def handler_string(self):
        if self._connected_channel is not None and self._connected_channel.handler_port is None:
            raise ValueError()

        return "http://" + str(self.host) + ":" + str(self.handler_port)

    def add_client_to_server(self, http_client):
        response = http_client.fetch(self.manager_string + "/clients/add")
        self.client_hash = response.body

    #def main_loop(self):
    #    if self.channel_hash is None:
    #        raise AssertionError("Sender needs to be initialized first")#

    #    http_client = httpclient.HTTPClient()

    #    while True:
    #        sound_buffer, length = self.recorder.get()
    #        parameters = {"buffer": sound_buffer}
    #        body = urllib.urlencode(parameters)
    #        http_client.fetch(self.handler_string + '/add',
    #                         method="POST", body=body)

    def terminate(self):
        if self.channel_hash is None:
            return

        http_client = httpclient.HTTPClient()
        self.remove_client_from_server(http_client)

    def remove_client_from_server(self, http_client):
        http_client.fetch(self.manager_string + "/clients/delete/" + self.channel_hash)
        self.channel_hash = None

    def get_settings(self, http_client):
        response = http_client.fetch(self.manager_string + "/channels/get")
        response_dict = json.loads(response.body)

        channel_information = response_dict[self.channel_hash]
        JSONPickleable.fill_with_json(self.player, channel_information)
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def set_name_of_client(self, http_client):
        parameters = {"name": self.name}
        body = urllib.urlencode(parameters)
        http_client.fetch(self.manager_string + "/clients/set/" + self.client_hash, body=body, method="POST")


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
    parser.add_argument("-c", "--channel_hash",
                        default=None,
                        type=str,
                        help="Channel hash to listen to.",
                        dest="channel_hash")
    args = parser.parse_args()
    listener = Listener(args.channel_hash, args.host, args.manager_port)
    listener.name = args.name
    listener.description = args.description
    listener.initialize()
    try:
        listener.main_loop()
    finally:
        listener.terminate()


if __name__ == "__main__":
    main()