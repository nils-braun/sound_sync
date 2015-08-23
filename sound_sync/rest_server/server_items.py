import datetime

from sound_sync.rest_server.json_pickable import JSONPickleable


class Channel(JSONPickleable):
    """
    Data structure for the channels
    """
    def __init__(self, item_hash):
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

        #: The used waiting time (FIXME: What is that?)
        self.waiting_time = "10"

        #: The added delay of the channel
        self.added_delay = "0"

        #: The used buffer size
        self.buffer_size = 1024

        #: The factor how often the buffer is fetched before returning the get function
        self.factor = 10



class Client(JSONPickleable):
    """
    Data structure for the clients
    """
    def __init__(self, item_hash):
        """
        Initialize with a given hash
        """
        JSONPickleable.__init__(self)

        #: The time of first login of the client
        self.login_time = datetime.datetime.now()

        #: The ip address of the client
        self.ip_address = None

        #: The name of the client
        self.name = ""

        #: The item has of the client in the client list
        self.item_hash = item_hash