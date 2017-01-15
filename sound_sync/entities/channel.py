class Channel:
    """
    Data structure for the channels
    """

    def __init__(self, item_hash=None):
        """
        Initialize with a given hash
        """
        #: The name of the channel
        self.name = ""

        #: The description of the channel (if any)
        self.description = ""

        #: The string of the now playing title
        self.now_playing = ""

        #: The item has of the channel in the channel list
        self.channel_hash = item_hash