import base64

from sound_sync.timing.time_utils import to_datetime
from struct import pack, unpack, calcsize


class SoundBufferWithTime:
    def __init__(self, sound_buffer, buffer_number, buffer_time):
        assert isinstance(sound_buffer, bytes)

        self.sound_buffer = sound_buffer
        self.buffer_time = buffer_time
        self.buffer_number = buffer_number
        self.sound_buffer_length = len(sound_buffer)

    @staticmethod
    def construct_from_string(string):
        buffer = base64.b64decode(string)

        sound_buffer, buffer = SoundBufferWithTime.unpack_helper(buffer)
        buffer_time_bytes_representation, buffer = SoundBufferWithTime.unpack_helper(buffer)
        buffer_number, sound_buffer_length = unpack("LL", buffer)

        assert sound_buffer_length == len(sound_buffer)

        new_sound_buffer = SoundBufferWithTime(
                sound_buffer=sound_buffer,
                buffer_number=buffer_number,
                buffer_time=to_datetime(str(buffer_time_bytes_representation, encoding="utf8")))

        return new_sound_buffer

    def to_string(self):
        buffer_time_byte_representation = str(self.buffer_time).encode("utf8")

        data = SoundBufferWithTime.pack_helper(self.sound_buffer)
        data += SoundBufferWithTime.pack_helper(buffer_time_byte_representation)
        data += pack("LL", self.buffer_number, self.sound_buffer_length)

        encoded_data = str(base64.b64encode(data), encoding="utf8")

        return encoded_data

    @staticmethod
    def unpack_helper(data):
        fmt = "I"
        size = calcsize(fmt)
        (length, ), data = unpack(fmt, data[:size]), data[size:]
        return data[:length], data[length:]

    @staticmethod
    def pack_helper(data):
        length = len(data)
        return pack("I%ds" % length, length, data)

    def __eq__(self, other):
        return (other.sound_buffer == self.sound_buffer and
                other.buffer_time == self.buffer_time and
                other.buffer_number == self.buffer_number and
                other.sound_buffer_length == self.sound_buffer_length)
