import json
import urllib

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
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

        #: A different manager string, only used for testing
        self._manager_string = None

    @property
    def manager_string(self):
        if self._manager_string is not None:
            return self._manager_string
        else:
            return "http://" + str(self.host) + ":" + str(self.manager_port)

    @manager_string.setter
    def manager_string(self, mock_url):
        self._manager_string = mock_url

    def send_to_url(self, url, content=None, method="POST"):
        if content:
            body = urllib.parse.urlencode(content)
            response = self.http_client.fetch(self.manager_string + url, body=body, method=method)
        else:
            response = self.http_client.fetch(self.manager_string + url)

        response.rethrow()
        return response

    def add_channel_to_server(self):
        response = self.send_to_url("/channels/add")
        channel_hash = str(response.body, encoding="utf8")
        return channel_hash

    def add_client_to_server(self):
        response = self.send_to_url("/clients/add")
        client_hash = str(response.body, encoding="utf8")
        return client_hash

    def remove_channel_from_server(self, channel_hash):
        self.send_to_url("/channels/delete/{channel_hash}".format(channel_hash=channel_hash))

    def remove_client_from_server(self, client_hash):
        self.send_to_url("/clients/delete/{client_hash}".format(client_hash=client_hash))

    def get_channel_information(self, channel_hash):
        response = self.send_to_url("/channels/get/{channel_hash}".format(channel_hash=channel_hash))
        response_dict = json.loads(str(response.body, encoding="utf8"))
        return response_dict

    def get_channels(self):
        response = self.send_to_url("/channels/get")
        response_dict = json.loads(str(response.body, encoding="utf8"))
        return response_dict

    def get_clients(self):
        response = self.send_to_url("/clients/get")
        response_dict = json.loads(str(response.body, encoding="utf8"))
        return response_dict

    def set_name_and_description_of_channel(self, name, description, channel_hash):
        parameters = {"name": name, "description": description}
        self.set_parameters_of_channel(parameters, channel_hash)

    def set_parameters_of_channel(self, parameters, channel_hash):
        self.send_to_url("/channels/set/{channel_hash}".format(channel_hash=channel_hash), parameters)

    def set_name_of_client(self, name, client_hash):
        parameters = {"name": name}
        self.send_to_url("/clients/set/{channel_hash}".format(channel_hash=client_hash), parameters)

    def add_buffer(self, sound_buffer, channel_hash):
        parameters = {"buffer": sound_buffer.to_string()}
        self.send_to_url("/buffers/{channel_hash}/add".format(channel_hash=channel_hash), parameters)

    def get_buffer(self, buffer_number, channel_hash):
        buffer = self.get_buffer_raw(buffer_number, channel_hash)
        return SoundBufferWithTime.construct_from_string(buffer)

    def get_buffer_raw(self, buffer_number, channel_hash):
        buffer = self.send_to_url("/buffers/{channel_hash}/get/{buffer_number}".format(channel_hash=channel_hash,
                                                                                       buffer_number=buffer_number))
        return str(buffer.body, encoding="utf8")

    def get_start_index(self, channel_hash):
        return self.get_buffer_index("start", channel_hash)

    def get_end_index(self, channel_hash):
        return self.get_buffer_index("end", channel_hash)

    def get_buffer_index(self, start_or_end, channel_hash):
        return int(self.send_to_url("/buffers/{channel_hash}/{start_or_end}".format(channel_hash=channel_hash,
                                                                                    start_or_end=start_or_end)).body)
