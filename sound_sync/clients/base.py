import urllib
try:
    from sound_sync.buffer_server import BufferList
except ImportError:
    from buffer_server import BufferList

from sound_sync.clients.connection import SoundSyncConnection
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Client, Channel
from sound_sync.timing.time_utils import get_current_date, waiting_time_to_datetime
from sound_sync.timing.waitForTimeProcess import Timer


class BaseListener(Client):
    def __init__(self, channel_hash=None, host=None, manager_port=None):
        Client.__init__(self)

        #: The connection to the rest server
        self.connection = SoundSyncConnection(host, manager_port)

        #: The channel hash of the channel we want to listen to
        self.channel_hash = channel_hash

        #: The channel we are listening to
        self._connected_channel = None

        #: The player to send the data to
        self.player = None

        #: The thread to handle the playing
        self.play_thread = None

        #: The list with the buffer from the server
        self.buffer_list = BufferList(100)

        #: The currently last played buffer number
        self.last_played_buffer_number = None

    def initialize(self):
        if self.client_hash is not None:
            return

        if self.channel_hash is None:
            raise ValueError()

        self.client_hash = self.connection.add_client_to_server()
        self.get_settings()
        self.connection.set_name_of_client(self.name, self.client_hash)

        self.player.initialize()

    @property
    def handler_string(self):
        if self._connected_channel is None or self._connected_channel.handler_port is None:
            raise ValueError()

        return "http://" + str(self.connection.host) + ":" + str(self._connected_channel.handler_port)

    def terminate(self):
        if self.client_hash is None:
            return

        self.connection.remove_client_from_server(self.client_hash)
        self.client_hash = None

        self.player.terminate()

    def get_settings(self):
        if self.channel_hash is None:
            raise ValueError()

        channel_information = self.connection.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.player, channel_information)
        self._connected_channel = Channel()
        JSONPickleable.fill_with_json(self._connected_channel, channel_information)

    def main_loop(self):
        if self.client_hash is None:
            raise AssertionError("Listener needs to be initialized first")

        current_start_index = self.get_current_buffer_start_index()
        self.buffer_list.set_start_index(current_start_index)

        # Receive as many packages as possible (to have a good starting point)
        self.initial_fill_buffer_list()

        # Start the thread to put sound buffers in the audio queue
        self.start_play_thread()

        # Receive information from the buffer server if possible
        while True:
            self.receive_and_add_next_buffer()

    def start_play_thread(self):
        next_play_time, next_buffer_number = self.calculate_next_starting_time_and_buffer()
        waiting_time = self.player.get_waiting_time()
        self.last_played_buffer_number = next_buffer_number - 1
        self.play_thread = Timer(next_play_time, waiting_time, self.play_next_buffer)
        self.play_thread.run()

    def initial_fill_buffer_list(self):
        # TODO: Maybe better: Do as many as possible
        # noinspection PyArgumentList
        current_start_index = self.buffer_list.get_start_index()
        next_play_time, next_buffer_number = self.calculate_next_starting_time_and_buffer()
        if next_buffer_number - current_start_index < 5:
            raise ValueError("Too few buffers loaded into the server.")

        for buffer_index in xrange(current_start_index, next_buffer_number - 1):
            self.receive_and_add_next_buffer()

    def receive_and_add_next_buffer(self):
        # noinspection PyArgumentList
        next_buffer_number = self.buffer_list.get_next_free_index()
        temp_buffer = self.get_buffer(next_buffer_number)
        self.buffer_list.add_buffer(temp_buffer)

    def play_next_buffer(self):
        next_buffer_number = self.last_played_buffer_number + 1
        next_buffer = self.buffer_list.get_buffer(str(next_buffer_number))
        self.player.put(next_buffer)

        self.last_played_buffer_number = next_buffer_number

    def calculate_next_starting_time_and_buffer(self):
        current_time = get_current_date()
        start_time = self.player.start_time

        waiting_time = self.player.get_waiting_time()

        if current_time < start_time:
            raise ValueError("Can not use start times in the future")

        time_delta = current_time - start_time
        number_of_passed_clocks = int(time_delta.total_seconds() / waiting_time)
        number_of_next_clock = number_of_passed_clocks + 1
        next_time = start_time + waiting_time_to_datetime(number_of_next_clock * waiting_time)

        return next_time, number_of_next_clock

    def get_current_buffer_start_index(self):
        response = self.connection.http_client.fetch(self.handler_string + "/start")
        if response.code == 200:
            return int(response.body)
        else:
            raise RuntimeError(response)

    def get_buffer(self, buffer_number):
        response = self.connection.http_client.fetch(self.handler_string + "/get/%d" % buffer_number, raise_error=False)
        if response.code == 200:
            return response.body
        else:
            raise RuntimeError(response)


class BaseSender(Channel):
    def __init__(self, host=None, manager_port=None):
        Channel.__init__(self)

        #: The connection to the rest server
        self.connection = SoundSyncConnection(host, manager_port)

        #: The recorder used for recording the sound data
        self.recorder = None

    def initialize(self):
        if self.channel_hash is not None:
            return

        self.channel_hash = self.connection.add_channel_to_server()
        self.get_settings()
        self.connection.set_name_and_description_of_channel(self.name, self.description, self.channel_hash)

        self.recorder.initialize()

    def main_loop(self):
        if self.channel_hash is None:
            raise AssertionError("Sender needs to be initialized first")

        while True:
            sound_buffer, length = self.recorder.get()
            parameters = {"buffer": sound_buffer}
            body = urllib.urlencode(parameters)
            self.connection.http_client.fetch(self.handler_string + '/add',
                                   method="POST", body=body)

    def terminate(self):
        if self.channel_hash is None:
            return

        self.connection.remove_channel_from_server(self.channel_hash)
        self.channel_hash = None

    def get_settings(self):
        channel_information = self.connection.get_channel_information(self.channel_hash)

        JSONPickleable.fill_with_json(self.recorder, channel_information)
        self.handler_port = channel_information["handler_port"]

    @property
    def handler_string(self):
        if self.handler_port is None:
            raise ValueError()

        return "http://" + str(self.connection.host) + ":" + str(self.handler_port)