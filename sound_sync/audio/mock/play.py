from sound_sync.audio.mock.device import MockDevice


class MockPlay(MockDevice):
    def __init__(self):
        super().__init__()

        self.buffer = []

    def put(self, sound_buffer):
        assert isinstance(sound_buffer, bytes)

        self.buffer.append(sound_buffer)

        print(sound_buffer)
