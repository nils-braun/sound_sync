from mock.mock import MagicMock

from sound_sync.audio.pcm.play import PCMPlay
from tests.fixtures import SoundTestCase


class TestPCMPlayer(SoundTestCase):
    def test_initialize(self):
        player = self.init_sound_player()

        self.alsaaudio.PCM.assert_called_with(device="default", type=self.PCM_PLAYBACK)

        player.pcm.setperiodsize.assert_called_with(2)
        player.pcm.setrate.assert_called_with(3)
        player.pcm.setchannels.assert_called_with(4)
        player.pcm.setformat.assert_called_with(self.PCM_FORMAT_S16_LE)

    def test_double_initialize(self):
        player = PCMPlay()
        player.pcm = 3

        player.initialize()
        self.assertEqual(player.pcm, 3)

    def test_terminate(self):
        player = PCMPlay()
        # Should not fail as pcm is none
        player.terminate()

        player = self.init_sound_player()

        player.terminate()

        player.pcm.close.assert_called_with()

    def test_put(self):
        player = PCMPlay()
        self.assertRaisesRegexp(ValueError, "^Device needs to be initialized first$",
                                player.put, "Buffer")

        test_buffer = bytes("This is a buffer", encoding="utf8")

        player = self.init_sound_player()
        player.pcm.write = MagicMock()

        player.put(test_buffer)

        player.pcm.write.assert_called_with(test_buffer)

    def test_put_with_errors(self):
        player = self.init_sound_player()

        def put_mock(buffer):
            raise Exception

        player.pcm.write = put_mock

        self.assertRaises(RuntimeError, player.put, bytes("This is a test buffer", encoding="utf8"))
