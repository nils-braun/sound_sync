class SoundDevice:
    def __init__(self):
        self.buffer_size = None
        self.channels = None
        self.frame_rate = None
        self.factor = None

        self.added_delay = None
        self.start_time = None

    def get_waiting_time(self):
        return float(self.factor) * float(self.buffer_size) / float(self.frame_rate)
