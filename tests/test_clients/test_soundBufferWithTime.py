import datetime
from unittest import TestCase

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime


class TestSoundBufferWithTime(TestCase):
    def test_construct_from_string(self):
        test_string = "This is<||>a test buf<||>2015-11-27 16:12:11.102030<||>42<||>21"
        new_sound_buffer = SoundBufferWithTime.construct_from_string(test_string)

        self.assertEqual(new_sound_buffer.sound_buffer_length, 21)
        self.assertEqual(new_sound_buffer.sound_buffer, "This is<||>a test buf")
        self.assertEqual(new_sound_buffer.buffer_number, 42)
        self.assertEqual(new_sound_buffer.buffer_time, datetime.datetime(2015, 11, 27, 16, 12, 11, 102030))

    def test_to_string(self):
        test_sound_buffer = "This is<||>a test buf"
        test_buffer_number = 42
        test_buffer_time = datetime.datetime(2015, 11, 27, 16, 12, 11, 102030)

        test_object = SoundBufferWithTime(sound_buffer=test_sound_buffer, buffer_number=test_buffer_number,
                                          buffer_time=test_buffer_time)

        expected_string = "This is<||>a test buf<||>2015-11-27 16:12:11.102030<||>42<||>21"

        self.assertEqual(test_object.to_string(), expected_string)

    def test_equality(self):
        test_string = "This is<||>a test buf<||>2015-11-27 16:12:11.102030<||>42<||>21"

        first_sound_buffer = SoundBufferWithTime.construct_from_string(test_string)
        second_sound_buffer = SoundBufferWithTime.construct_from_string(test_string)

        self.assertEqual(first_sound_buffer, second_sound_buffer)
        self.assertEqual(first_sound_buffer, first_sound_buffer)
        self.assertEqual(second_sound_buffer, second_sound_buffer)

        test_sound_buffer = "This is<||>a test buf"
        test_buffer_number = 42
        test_buffer_time = datetime.datetime(2015, 11, 27, 16, 12, 11, 102030)

        first_sound_buffer = SoundBufferWithTime(sound_buffer=test_sound_buffer, buffer_number=test_buffer_number,
                                                buffer_time=test_buffer_time)

        second_sound_buffer = SoundBufferWithTime(sound_buffer=test_sound_buffer, buffer_number=test_buffer_number,
                                                  buffer_time=test_buffer_time)

        self.assertEqual(first_sound_buffer, second_sound_buffer)
        self.assertEqual(first_sound_buffer, first_sound_buffer)
        self.assertEqual(second_sound_buffer, second_sound_buffer)

        first_sound_buffer.buffer_time = datetime.datetime(2016, 11, 27, 16, 12, 11, 102030)
        self.assertNotEqual(first_sound_buffer, second_sound_buffer)

        first_sound_buffer.buffer_time = datetime.datetime(2015, 11, 27, 16, 12, 11, 102030)
        self.assertEqual(first_sound_buffer, second_sound_buffer)
        first_sound_buffer.sound_buffer = "Other string"
        self.assertNotEqual(first_sound_buffer, second_sound_buffer)

        first_sound_buffer.sound_buffer = test_sound_buffer
        self.assertEqual(first_sound_buffer, second_sound_buffer)
        first_sound_buffer.buffer_number = 30
        self.assertNotEqual(first_sound_buffer, second_sound_buffer)
