import datetime

class SoundDevice:
    """
    Data structure for every device handling sound
    """
    def __init__(self):
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

        #: The starting time of the channel as a common reference
        self.start_time = datetime.datetime.now()

    def get_waiting_time(self):
        return float(self.factor) * float(self.buffer_size) / float(self.frame_rate)
