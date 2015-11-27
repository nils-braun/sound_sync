from unittest import TestCase

import datetime

from sound_sync.audio.sound_device import SoundDevice


class TestSoundDevice(TestCase):
    def test_get_waiting_time(self):
        sound_device = SoundDevice()

        self.assertEqual(sound_device.get_waiting_time(), datetime.timedelta(seconds=10240.0/44100))

        sound_device.buffer_size = 100
        sound_device.factor = 200
        sound_device.frame_rate = 20

        self.assertEqual(sound_device.get_waiting_time(), datetime.timedelta(seconds=1000))

    def test_standard_settings(self):
        sound_device = SoundDevice()

        self.assertEqual(sound_device.added_delay, "0")
        self.assertEqual(sound_device.channels, "2")
        self.assertEqual(sound_device.frame_rate, "44100")
        self.assertEqual(sound_device.buffer_size, 1024)
        self.assertEqual(sound_device.factor, 10)