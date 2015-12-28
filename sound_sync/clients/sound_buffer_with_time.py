from sound_sync.timing.time_utils import to_datetime


class SoundBufferWithTime():
    SPLIT_SEPARATOR = "<||>"

    def __init__(self, sound_buffer, buffer_number, buffer_time):
        self.sound_buffer = sound_buffer
        self.buffer_time = buffer_time
        self.buffer_number = buffer_number
        self.sound_buffer_length = len(sound_buffer)

    @staticmethod
    def construct_from_string(string):
        splitted_information = string.split(SoundBufferWithTime.SPLIT_SEPARATOR)

        new_sound_buffer = SoundBufferWithTime(
            sound_buffer=SoundBufferWithTime.SPLIT_SEPARATOR.join(splitted_information[:-3]),
            buffer_number=int(splitted_information[-2]),
            buffer_time=to_datetime(splitted_information[-3]))

        sound_buffer_length = int(splitted_information[-1])
        assert new_sound_buffer.sound_buffer_length == sound_buffer_length

        return new_sound_buffer

    def to_string(self):
        return_string = SoundBufferWithTime.SPLIT_SEPARATOR.join([self.sound_buffer,
                                                                  str(self.buffer_time),
                                                                  str(self.buffer_number),
                                                                  str(self.sound_buffer_length)])

        return return_string
