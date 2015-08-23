import json
import urllib
from tornado import httpclient
from sound_sync.audio.pcm.record import PCMRecorder


class Sender:
    def __init__(self):
        self.http_client = httpclient.AsyncHTTPClient()
        self.host = "localhost"
        self.port = 8888
        self.channel_hash = None
        self.recorder = PCMRecorder()

        self.name = ""
        self.description = ""

    @property
    def server_string(self):
        return "http://" + str(self.host) + ":" + str(self.port)

    def add_channel_to_server(self, http_client):
        response = http_client.fetch(self.server_string + "/channels/add")
        self.channel_hash = response.body

    def initialize(self):
        if self.channel_hash is not None:
            return

        http_client = httpclient.HTTPClient()

        try:
            self.add_channel_to_server(http_client)
            self.get_sound_settings(http_client)
            self.set_name_and_description_of_channel(http_client)
        except httpclient.HTTPError as e:
            print("Error: " + str(e))

        self.recorder.initialize()

    def main_loop(self):
        if self.channel_hash is None:
            raise AssertionError("Sender needs to be initialized first")

        http_client = httpclient.HTTPClient()

        buffer_number = 0

        while True:
            sound_buffer, length = self.recorder.get()
            parameters = {"buffer": sound_buffer}
            body = urllib.urlencode(parameters)
            response = http_client.fetch(self.server_string + '/channels/' + self.channel_hash + '/buffers/add',
                                         method="POST", body=body)

            assert buffer_number == int(response.body)
            buffer_number += 1

    def terminate(self):
        if self.channel_hash is None:
            return

        http_client = httpclient.HTTPClient()

        try:
            self.remove_channel_from_server(http_client)
        except httpclient.HTTPClient as e:
            print("Error: " + str(e))

    def remove_channel_from_server(self, http_client):
        http_client.fetch(self.server_string + "/channels/delete/" + self.channel_hash)
        self.channel_hash = None

    def get_sound_settings(self, http_client):
        response = http_client.fetch(self.server_string + "/channels/get")
        response_dict = json.loads(response.body)

        channel_information = response_dict[self.channel_hash]
        self.recorder.buffer_size = channel_information["buffer_size"]
        self.recorder.frame_rate = channel_information["frame_rate"]
        self.recorder.channels = channel_information["channels"]
        self.recorder.factor = channel_information["factor"]

    def set_name_and_description_of_channel(self, http_client):
        parameters = {"name": self.name,
                      "description": self.description}
        body = urllib.urlencode(parameters)
        http_client.fetch(self.server_string + "/channels/set/" + self.channel_hash, body=body, method="POST")


if __name__ == "__main__":
    sender = Sender()
    sender.name = "Name"
    sender.description = "Description"
    sender.initialize()

    try:
        sender.main_loop()
    finally:
        sender.terminate()