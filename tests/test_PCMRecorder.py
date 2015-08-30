from unittest import TestCase
from sound_sync.audio.pcm.record import PCMRecorder
from mock.mock import patch


class TestPCMRecorder(TestCase):
    def setUp(self):
        patcher = patch("sound_sync.audio.pcm.device.alsaaudio")
        self.alsaaudio = patcher.start()
        self.addCleanup(patcher.stop)

    def init_sound_recorder(self):
        recorder = PCMRecorder()
        self.alsaaudio.cards = lambda: ["TestCard", "Loopback", "Bla"]
        self.alsaaudio.PCM_CAPTURE = 372435
        self.alsaaudio.PCM_FORMAT_S16_LE = 21654
        recorder.buffer_size = 2
        recorder.frame_rate = 3
        recorder.channels = 4
        recorder.factor = 5
        recorder.initialize()
        return recorder

    def test_initialize(self):
        recorder = self.init_sound_recorder()

        self.alsaaudio.PCM.assert_called_with(type=372435, device="hw:Loopback,1,0")

        recorder.pcm.setchannels.assert_called_with(4)
        recorder.pcm.setrate.assert_called_with(3)
        recorder.pcm.setformat.assert_called_with(21654)
        recorder.pcm.setperiodsize.assert_called_with(2)

        recorder = PCMRecorder()
        recorder.pcm = 3

        recorder.initialize()
        self.assertEqual(recorder.pcm, 3)

    def test_assert_loopback_device(self):
        self.assertRaises(ValueError, PCMRecorder.assert_loopback_device)
        # noinspection PyUnresolvedReferences
        self.alsaaudio.cards.assert_called_with()

        self.alsaaudio.cards = lambda: ["TestCard", "Loopback", "Bla"]
        try:
            PCMRecorder.assert_loopback_device()
        except ValueError:
            self.fail()

    def test_terminate(self):
        recorder = PCMRecorder()
        # Should not fail as pcm is none
        recorder.terminate()

        recorder = self.init_sound_recorder()
        recorder.terminate()

        recorder.pcm.close.assert_called_with()

    def test_get(self):
        recorder = PCMRecorder()
        self.assertRaises(ValueError, recorder.get)

        recorder = self.init_sound_recorder()
        recorder.pcm.read = lambda: (8234234, "This is a buffer")  # length, buffer

        sound_buffer, length = recorder.get()
        self.assertEqual(sound_buffer, "This is a buffer"*5)
        self.assertEqual(length, 8234234*5)