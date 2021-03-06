import atexit
import socket

from sound_sync.audio.sound_device import SoundDevice
from sound_sync.rest_server.server_items.buffer_server_process import BufferServerProcess
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable
from sound_sync.timing.time_utils import get_current_date


class Channel(JSONPickleable):
    """
    Data structure for the channels
    """

    def __init__(self, item_hash=None, request=None):
        """
        Initialize with a given hash
        """
        JSONPickleable.__init__(self)

        #: The name of the channel
        self.name = ""

        #: The description of the channel (if any)
        self.description = ""

        #: The string of the now playing title
        self.now_playing = ""

        #: The item has of the channel in the channel list
        self.channel_hash = item_hash


class ChannelItem(Channel, SoundDevice):
    """
    Data structure for channels handled by the server (with a added background process and sound information)
    Note: ClientPrograms (as the sender or the listener) use only the Channel datastructure, not the ChannelClient
    as they add a SoundDevice by themselves and do not need the handler process
    """

    def __init__(self, item_hash, request):
        Channel.__init__(self, item_hash, request)
        SoundDevice.__init__(self)

        # Set handler port and start time to a defined value when initializing this on the server.
        self.handler_port = 8888
        self.start_time = get_current_date()

        #: The handler process
        self._process = None

        self.start_process()

    def start_process(self):
        """ Start the buffer server as a background process """
        self._process = BufferServerProcess(self.handler_port)
        self._process.start()
        atexit.register(self.stop)

    def stop(self):
        """ Stop the background server """
        self._process.terminate()


class Client(JSONPickleable):
    """
    Data structure for the clients
    """

    def __init__(self, item_hash=None, request=None):
        """
        Initialize with a given hash
        """
        JSONPickleable.__init__(self)

        #: The name of the client
        self.name = ""

        #: The item has of the client in the client list
        self.client_hash = item_hash


class ClientItem(Client):
    """
    Data structure for the clients handled by the server (with added meta information)
    """

    def __init__(self, item_hash, request):
        Client.__init__(self, item_hash, request)

        #: The time of first login of the client
        self.login_time = get_current_date()

        #: The ip address of the client
        self.ip_address = request.headers["Host"]

    def stop(self):
        """ Unused """
        pass
