class SoundDevice:
    def __init__(self):
        self.buffer_size = None
        self.channels = None
        self.frame_rate = None

    def initialize(self):
        pass

    def terminate(self):
        pass


class SoundRecorder(SoundDevice):
    def get(self):
        pass


class SoundPlayer(SoundDevice):
    def put(self, sound_buffer):
        pass