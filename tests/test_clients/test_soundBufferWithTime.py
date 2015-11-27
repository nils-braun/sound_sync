from unittest import TestCase

import datetime

from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime


class TestSoundBufferWithTime(TestCase):
    def test_construct_from_string(self):
        self.fail()

    def test_to_string(self):
        test_sound_buffer = "This is a test buffer"
        test_sound_buffer_length = len(test_sound_buffer)
        test_buffer_number = 42
        test_buffer_time = datetime.datetime(2015, 11, 27, 16, 12, 11, 102030)

        test_object = SoundBufferWithTime(sound_buffer=test_sound_buffer, buffer_number=test_buffer_number,
                                          buffer_time=test_buffer_time)

        expected_string = "This is a test buffer<||>2015-11-27 16:12:11.102030<||>42<||>21"

        self.assertEqual(test_object.to_string(), expected_string)
