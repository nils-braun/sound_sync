from sound_sync.timing.time_utils import to_datetime


class SoundBufferWithTime():
    SPLIT_SEPARATOR = "<||>"

    def __init__(self, sound_buffer=None, buffer_number=None, buffer_time=None):
        self.sound_buffer = sound_buffer
        self.buffer_time = buffer_time
        self.buffer_number = buffer_number
        self.sound_buffer_length = len(sound_buffer)

    def construct_from_string(self, string):
        splitted_information = string.split(SoundBufferWithTime.SPLIT_SEPARATOR)

        self.sound_buffer_length = int(splitted_information[-1])
        self.buffer_number = int(splitted_information[-2])
        self.buffer_time = to_datetime(splitted_information[-3])
        self.sound_buffer = "".join(splitted_information[:-4])

        assert len(self.sound_buffer) == self.sound_buffer_length

    def to_string(self):
        return_string = SoundBufferWithTime.SPLIT_SEPARATOR.join([self.sound_buffer,
                                                                  str(self.buffer_time), 
                                                                  str(self.buffer_number),
                                                                  str(self.sound_buffer_length)])

        return return_string
