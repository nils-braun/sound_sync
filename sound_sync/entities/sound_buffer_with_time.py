import base64

from sound_sync.timing.time_utils import to_datetime
from struct import pack, unpack, calcsize


def packer(types, *variables, prefix="!"):
    """
    Helper function to pack variables of certain types into
    their binary representation and encode everything with b64.
    :param types: The types of the variables as list. Must be as long as the following variables list.
     Currently, only "int" and "bytes" are valid types.
    :param variables: The variables to encode.
    :param prefix: The prefix to use. Look into the documentation of struct to see their meaning.
    :return: The b64-encoded binary representation of the variables.
    """
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
    """
    Helper function to unpack variables from a string, which includes the b64-encoded
    binary representation of some variables (produced with pack).
    :param types: The types of the variables that are in the string.
    :param string: The string with the representation.
    :param prefix: The prefix, which was used while packing.
    :return: The extracted variables (as many as there are types).
    """
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
    """
    Base entity for transporting and storing a sound buffer
    together with its recording time (of the start) and
    its buffer number.
    Can be constructed from and into a string, which is an utf-8 encoded version
    of a binary representation of the class.
    """
    def __init__(self, sound_buffer, buffer_number, buffer_time):
        """
        Constructor from sound data.
        :param sound_buffer: The sound data as bytes.
        :param buffer_number: The buffer number.
        :param buffer_time: The recording time as a datetime object.
        """
        assert isinstance(sound_buffer, bytes)

        self.sound_buffer = sound_buffer
        self.buffer_time = buffer_time
        self.buffer_number = buffer_number

        # Store the sound buffer length for failure detection during communication.
        self.sound_buffer_length = len(sound_buffer)

    @staticmethod
    def construct_from_string(string):
        """
        Use the utf-8 encoded version of the binary representation
        of a sound buffer, to create a SoundBufferWithTime object.
        :param string: The binary representation in utf8 encoding.
        :return: A SoundBufferWithTime object from the data.
        """
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
        """
        Encode the sound buffer into its binary representation
        and this representation into an utf-8 encoded string.
        Can be used for transporting the object.
        :return: The string with the binary representation.
        """
        buffer_time_byte_representation = str(self.buffer_time).encode("utf8")

        encoded_string = packer([bytes, bytes, int, int],
                                self.sound_buffer,
                                buffer_time_byte_representation,
                                self.buffer_number,
                                self.sound_buffer_length)

        return encoded_string

    def __eq__(self, other):
        """Equality operator"""
        return (other.sound_buffer == self.sound_buffer and
                other.buffer_time == self.buffer_time and
                other.buffer_number == self.buffer_number and
                other.sound_buffer_length == self.sound_buffer_length)
