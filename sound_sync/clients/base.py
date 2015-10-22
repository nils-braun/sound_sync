import json
import urllib
from tornado import httpclient
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Client, Channel


class SoundSyncConnector:
    """
    Class to handle the connection to the sound sync server from a client.
    """
    def __init__(self, host=None, manager_port=None):

        #: The port of the manager host
        self.manager_port = manager_port

        #: The address of the manager host
        self.host = host

        #: A http client to use (for free ;-)
        self.http_client = httpclient.HTTPClient()

    @property
    def manager_string(self):
        return "http://" + str(self.host) + ":" + str(self.manager_port)

    def add_channel_to_server(self):
        response = self.http_client.fetch(self.manager_string + "/channels/add")
        channel_hash = response.body
        return channel_hash

    def add_client_to_server(self):
        response = self.http_client.fetch(self.manager_string + "/clients/add")
        client_hash = response.body
        return client_hash

    def remove_channel_from_server(self, channel_hash):
        self.http_client.fetch(self.manager_string + "/channels/delete/" + channel_hash)

    def remove_client_from_server(self, client_hash):
        self.http_client.fetch(self.manager_string + "/clients/delete/" + client_hash)

    def set_name_and_description_of_channel(self, name, description, channel_hash):
        parameters = {"name": name,
                      "description": description}
        body = urllib.urlencode(parameters)
        self.http_client.fetch(self.manager_string + "/channels/set/" + channel_hash, body=body, method="POST")

    def set_name_of_client(self, name, client_hash):
        parameters = {"name": name}
        body = urllib.urlencode(parameters)
        self.http_client.fetch(self.manager_string + "/clients/set/" + client_hash, body=body, method="POST")

    def get_channel_information(self, channel_hash):
        response = self.http_client.fetch(self.manager_string + "/channels/get")
        response_dict = json.loads(response.body)
        return response_dict[channel_hash]


class BaseListener(Client, SoundSyncConnector):
    def __init__(self, channel_hash=None, host=None, manager_port=None):
        Client.__init__(self)
        SoundSyncConnector.__init__(self, host, manager_port)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The channel we are listening to
        self._connected_channel = None

        #: The player to send the data to
        self.player = None

    def initialize(self):
        if self.client_hash is not None:
            return

        self.client_hash = self.add_client_to_server()
        self.get_settings()
        self.set_name_of_client(self.name, self.client_hash)

        self.player.initialize()

    @property
    def handler_string(self):
        if self._connected_channel is None or self._connected_channel.handler_port is None:
            raise ValueError()

        return "http://" + str(self.host) + ":" + str(self._connected_channel.handler_port)

    def terminate(self):
        if self.client_hash is None:
            return

        self.remove_client_from_server(self.client_hash)
        self.client_hash = None

        self.player.terminate()

    def get_settings(self):
        channel_information = self.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def main_loop(self):
        if self.client_hash is None:
            raise AssertionError("Listener needs to be initialized first")

        # Receive as many packages as possible (to have a good starting point)

        # Start the thread to put sound buffers in the audio queue

        # Receive information from the buffer server if possible


class BaseSender(Channel, SoundSyncConnector):
    def __init__(self, host=None, manager_port=None):
        Channel.__init__(self)
        SoundSyncConnector.__init__(self, host, manager_port)

        #: The recorder used for recording the sound data
        self.recorder = None

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