from buffer_server import BufferList

from sound_sync.clients.buffer_downloader_thread import BufferDownloaderThread
from sound_sync.clients.buffer_player_thread import BufferPlayerThread
from sound_sync.clients.connection import SoundSyncConnection
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.rest_server.server_items.server_items import Client, Channel


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

        self.buffer_list = BufferList(100)

        #: The threads to handle the playing
        self.downloader_thread = BufferDownloaderThread(self)

        self.player_thread = BufferPlayerThread(self)

        #: The last played buffer
        self.last_played_buffer_number = -1

    def initialize(self):
        if self.client_hash is not None:
            return

        if self.channel_hash is None:
            raise ValueError()

        self.client_hash = self.connection.add_client_to_server()
        self.get_settings()
        self.connection.set_name_of_client(self.name, self.client_hash)

        self.player.initialize()

    def terminate(self):
        if self.client_hash is None:
            return

        self.player.terminate()
        self.player_thread.terminate()
        self.downloader_thread.terminate()

        self.connection.remove_client_from_server(self.client_hash)
        self.client_hash = None

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

        # We do not need both of them to run as anther thread. We choose the downloader thread as our one.
        self.player_thread.start()
        self.downloader_thread.run()

