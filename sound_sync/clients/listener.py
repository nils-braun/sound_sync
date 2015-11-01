import argparse
import time
import datetime
from sound_sync.timing.waitForTimeProcess import Timer

from sound_sync.clients.base import SoundSyncConnector
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.rest_server.server_items.server_items import Client, Channel


class Listener(Client, SoundSyncConnector):
    def __init__(self, channel_hash=None, host=None, manager_port=None):
        Client.__init__(self)
        SoundSyncConnector.__init__(self, host, manager_port)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The recorder used for recording the sound data
        self.player = PCMPlay()

        #: The channel we are listening to
        self._connected_channel = None

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

    def main_loop(self):
        if self.client_hash is None:
            raise AssertionError("Listener needs to be initialized first")

        # Receive as many packages as possible (to have a good starting point)

        # Start the thread to put sound buffers in the audio queue
        time_thread = Timer()

        # Receive information from the buffer server if possible

    def calculate_next_starting_time_and_buffer(self):
        current_time = datetime.datetime.now()
        start_time = self.player.start_time

        waiting_time = self.player.get_waiting_time()

        if current_time < start_time:
            raise ValueError("Can not use start times in the future")

        time_delta = current_time - start_time
        number_of_passed_clocks = int(time_delta.total_seconds() % waiting_time)
        next_time = start_time + number_of_passed_clocks * waiting_time

        return next_time, number_of_passed_clocks

    def terminate(self):
        if self.client_hash is None:
            return

        self.remove_client_from_server(self.client_hash)
        self.client_hash = None

    def get_settings(self):
        channel_information = self.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)


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