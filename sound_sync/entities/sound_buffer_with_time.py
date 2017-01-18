import base64

from sound_sync.timing.time_utils import to_datetime
from struct import pack, unpack, calcsize


def packer(types, *variables, prefix="!"):
    data = bytes()
    for type, variable in zip(types, variables):
        if type == bytes:
            variable_length = len(variable)
            data += pack(prefix + "I", variable_length)
            data += pack(prefix + "%ds" % variable_length, variable)
        elif type == int:
            data += pack(prefix + "L", variable)
        else:
            raise TypeError

    return base64.b64encode(data)

def unpacker(types, string, prefix="!"):
    data = base64.b64decode(string)

    return_variables = []
    for type in types:
        if type == bytes:
            format = prefix + "I"
            size = calcsize(format)

            (variable_length,) = unpack(format, data[:size])
            variable = data[size:size + variable_length]

            return_variables.append(variable)

            data = data[size + variable_length:]
        elif type == int:
            format = prefix + "L"
            size = calcsize(format)

            (variable,) = unpack(format, data[:size])

            return_variables.append(variable)

            data = data[size:]
        else:
            raise TypeError

    return return_variables


class SoundBufferWithTime:
    def __init__(self, sound_buffer, buffer_number, buffer_time):
        assert isinstance(sound_buffer, bytes)

        self.sound_buffer = sound_buffer
        self.buffer_time = buffer_time
        self.buffer_number = buffer_number
        self.sound_buffer_length = len(sound_buffer)

    @staticmethod
    def construct_from_string(string):
        variables = unpacker([bytes, bytes, int, int], string)
        sound_buffer, buffer_time_bytes_representation, buffer_number, sound_buffer_length = variables

        buffer_type = to_datetime(str(buffer_time_bytes_representation, encoding="utf8"))

        assert sound_buffer_length == len(sound_buffer)

        new_sound_buffer = SoundBufferWithTime(
                sound_buffer=sound_buffer,
                buffer_number=buffer_number,
                buffer_time=buffer_type)

        return new_sound_buffer

    def to_string(self):
        buffer_time_byte_representation = str(self.buffer_time).encode("utf8")

        encoded_string = packer([bytes, bytes, int, int],
                                self.sound_buffer,
                                buffer_time_byte_representation,
                                self.buffer_number,
                                self.sound_buffer_length)

        return encoded_string

    def __eq__(self, other):
        return (other.sound_buffer == self.sound_buffer and
                other.buffer_time == self.buffer_time and
                other.buffer_number == self.buffer_number and
                other.sound_buffer_length == self.sound_buffer_length)
