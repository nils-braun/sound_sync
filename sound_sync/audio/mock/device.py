from sound_sync.audio.sound_device import SoundDevice


class MockDevice(SoundDevice):
    def __init__(self):
        SoundDevice.__init__(self)

    def terminate(self):
        pass

    def initialize(self):
        pass