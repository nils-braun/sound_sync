import datetime
from unittest import TestCase

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime, packer, unpacker


class TestSoundBufferWithTime(TestCase):
    def test_conversion(self):
        test_sound_buffer = bytes("This is<||>a test buf", encoding="utf8")
        test_buffer_number = 42
        test_buffer_time = datetime.datetime(2015, 11, 27, 16, 12, 11, 102030)

        test_object = SoundBufferWithTime(sound_buffer=test_sound_buffer, buffer_number=test_buffer_number,
                                          buffer_time=test_buffer_time)

        bytes_representation = test_object.to_string()

        result_object = SoundBufferWithTime.construct_from_string(bytes_representation)

        self.assertEqual(result_object, test_object)
        self.assertEqual(result_object.buffer_number, test_object.buffer_number)
        self.assertEqual(result_object.buffer_time, test_object.buffer_time)
        self.assertEqual(result_object.sound_buffer, test_object.sound_buffer)
        self.assertEqual(result_object.sound_buffer_length, test_object.sound_buffer_length)

    def test_equality(self):
        test_sound_buffer = bytes("This is<||>a test buf", encoding="utf8")
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


class TestPackerAndUnpacker(TestCase):
    def test_wrong_types(self):
        class MyClass:
            pass

        correct_string = packer([int], 3)

        a = MyClass()

        self.assertRaises(TypeError, packer, [float], 1.0)
        self.assertRaises(TypeError, unpacker, [float], correct_string)

        self.assertRaises(TypeError, packer, [MyClass], a)
        self.assertRaises(TypeError, unpacker, [MyClass], correct_string)