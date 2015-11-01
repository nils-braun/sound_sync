import json
import urllib
from tornado import httpclient

__author__ = 'nils'


class SoundSyncConnection:
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