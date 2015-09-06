import json
import urllib
from tornado import httpclient


class Sender:
    def __init__(self):
        from sound_sync.audio.pcm.record import PCMRecorder

        self.http_client = httpclient.AsyncHTTPClient()
        self.host = None
        self.manager_port = None
        self.handler_port = None
        self.channel_hash = None
        self.recorder = PCMRecorder()

        self.name = None
        self.description = None

    def initialize(self):
        if self.channel_hash is not None:
            return

        http_client = httpclient.HTTPClient()

        self.add_channel_to_server(http_client)
        self.get_settings(http_client)
        self.set_name_and_description_of_channel(http_client)
        self.recorder.initialize()

    @property
    def manager_string(self):
        return "http://" + str(self.host) + ":" + str(self.manager_port)

    @property
    def handler_string(self):
        if self.handler_port is None:
            raise ValueError()

        return "http://" + str(self.host) + ":" + str(self.handler_port)

    def add_channel_to_server(self, http_client):
        response = http_client.fetch(self.manager_string + "/channels/add")
        self.channel_hash = response.body

    def main_loop(self):
        if self.channel_hash is None:
            raise AssertionError("Sender needs to be initialized first")

        http_client = httpclient.HTTPClient()

        while True:
            sound_buffer, length = self.recorder.get()
            parameters = {"buffer": sound_buffer}
            body = urllib.urlencode(parameters)
            http_client.fetch(self.handler_string + '/add',
                              method="POST", body=body)

    def terminate(self):
        if self.channel_hash is None:
            return

        http_client = httpclient.HTTPClient()

        self.remove_channel_from_server(http_client)

    def remove_channel_from_server(self, http_client):
        http_client.fetch(self.manager_string + "/channels/delete/" + self.channel_hash)
        self.channel_hash = None

    def get_settings(self, http_client):
        response = http_client.fetch(self.manager_string + "/channels/get")
        response_dict = json.loads(response.body)

        channel_information = response_dict[self.channel_hash]
        self.recorder.buffer_size = channel_information["buffer_size"]
        self.recorder.frame_rate = channel_information["frame_rate"]
        self.recorder.channels = channel_information["channels"]
        self.recorder.factor = channel_information["factor"]
        self.handler_port = channel_information["handler_port"]

    def set_name_and_description_of_channel(self, http_client):
        parameters = {"name": self.name,
                      "description": self.description}
        body = urllib.urlencode(parameters)
        http_client.fetch(self.manager_string + "/channels/set/" + self.channel_hash, body=body, method="POST")


if __name__ == "__main__":
    import argparse

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

    sender = Sender()
    sender.host = args.hostname
    sender.manager_port = args.manager_port
    sender.name = args.name
    sender.description = args.description
    sender.initialize()

    try:
        sender.main_loop()
    finally:
        sender.terminate()