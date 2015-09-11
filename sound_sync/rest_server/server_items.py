import atexit
import datetime
import socket
from subprocess import Popen

from sound_sync.rest_server.json_pickable import JSONPickleable


def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class Channel(JSONPickleable):
    """
    Data structure for the channels
    """
    def __init__(self, item_hash, request):
        """
        Initialize with a given hash
        """
        JSONPickleable.__init__(self)

        #: The starting time of the channel as a common reference
        self.start_time = datetime.datetime.now()

        #: The name of the channel
        self.name = ""

        #: The description of the channel (if any)
        self.description = ""

        #: The string of the now playing title
        self.now_playing = ""

        #: The item has of the channel in the channel list
        self.item_hash = item_hash

        #: The number of speaker channels
        self.channels = "2"

        #: The used frame rate
        self.frame_rate = "44100"

        #: The used waiting time
        self.waiting_time = "10"

        #: The added delay of the channel
        self.added_delay = "0"

        #: The used buffer size
        self.buffer_size = 1024

        #: The factor how often the buffer is fetched before returning the get function
        self.factor = 10

        #: The buffer_handler server we are handling
        self.handler_port = get_free_port()

        #: The handler process
        self._process = None

        self.start_buffer_handler()

    def stop(self):
        self._process.kill()

    def start_buffer_handler(self):
        self._process = Popen(["./buffer_server/build/buffer_server", str(self.handler_port)])
        atexit.register(self.stop)


class Client(JSONPickleable):
    """
    Data structure for the clients
    """
    def __init__(self, item_hash, request):
        """
        Initialize with a given hash
        """
        JSONPickleable.__init__(self)

        #: The time of first login of the client
        self.login_time = datetime.datetime.now()

        #: The ip address of the client
        self.ip_address = request.headers["Host"]

        #: The name of the client
        self.name = ""

        #: The item has of the client in the client list
        self.item_hash = item_hash

    def stop(self):
        pass