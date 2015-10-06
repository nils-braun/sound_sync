from unittest import TestCase
from sound_sync.audio.sound_device import SoundDevice


class TestSoundDevice(TestCase):
    def test_get_waiting_time(self):
        sound_device = SoundDevice()

        self.assertEqual(sound_device.get_waiting_time(), 10240.0/44100)

        sound_device.buffer_size = 100
        sound_device.factor = 200
        sound_device.frame_rate = 20

        self.assertEqual(sound_device.get_waiting_time(), 1000)
