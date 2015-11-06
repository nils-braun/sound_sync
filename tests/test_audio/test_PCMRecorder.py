from sound_sync.audio.pcm.record import PCMRecorder
from tests.fixtures import SoundTestCase


class TestPCMRecorder(SoundTestCase):
    def test_initialize(self):
        recorder = self.init_sound_recorder()

        self.alsaaudio.PCM.assert_called_with(type=self.PCM_CAPTURE, device="hw:Loopback,1,0")

        recorder.pcm.setperiodsize.assert_called_with(2)
        recorder.pcm.setrate.assert_called_with(3)
        recorder.pcm.setchannels.assert_called_with(4)
        recorder.pcm.setformat.assert_called_with(self.PCM_FORMAT_S16_LE)

    def test_double_initialize(self):
        recorder = PCMRecorder()
        recorder.pcm = 3

        recorder.initialize()
        self.assertEqual(recorder.pcm, 3)

    def test_assert_loopback_device(self):
        self.assertRaises(ValueError, PCMRecorder.assert_loopback_device)
        # noinspection PyUnresolvedReferences
        self.alsaaudio.cards.assert_called_with()

        self.alsaaudio.cards = lambda: ["TestCard", "Loopback", "Bla"]
        PCMRecorder.assert_loopback_device()

    def test_terminate(self):
        recorder = PCMRecorder()
        # Should not fail as pcm is none
        recorder.terminate()

        recorder = self.init_sound_recorder()
        recorder.terminate()

        recorder.pcm.close.assert_called_with()

    def test_get(self):
        recorder = PCMRecorder()
        recorder.factor = 1
        self.assertRaises(ValueError, recorder.get)

        recorder = self.init_sound_recorder()
        test_buffer_length = 8234234
        test_buffer = "This is a buffer"
        test_factor = 6

        recorder.factor = test_factor

        recorder.pcm.read = lambda: (test_buffer_length, test_buffer)  # length, buffer
        sound_buffer, length = recorder.get()
        self.assertEqual(sound_buffer, test_buffer*test_factor)
        self.assertEqual(length, test_buffer_length*test_factor)