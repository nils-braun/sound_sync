from unittest import TestCase
from sound_sync.audio.pcm.play import PCMPlay
from mock.mock import patch, MagicMock


class TestPCMPlayer(TestCase):
    def setUp(self):
        patcher = patch("sound_sync.audio.pcm.device.alsaaudio")
        self.alsaaudio = patcher.start()
        self.addCleanup(patcher.stop)

    def init_sound_player(self):
        player = PCMPlay()
        self.alsaaudio.PCM_PLAYBACK = 372435
        self.alsaaudio.PCM_FORMAT_S16_LE = 21654
        self.alsaaudio.PCM_NONBLOCKING = 21354
        player.buffer_size = 2
        player.frame_rate = 3
        player.channels = 4
        player.factor = 5
        player.initialize()
        return player

    def test_initialize(self):
        player = self.init_sound_player()

        self.alsaaudio.PCM.assert_called_with(device="default", type=372435, mode=21354)

        player.pcm.setchannels.assert_called_with(4)
        player.pcm.setrate.assert_called_with(3)
        player.pcm.setformat.assert_called_with(21654)
        player.pcm.setperiodsize.assert_called_with(2)

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
        self.assertRaises(ValueError, player.put, "Buffer")

        player = self.init_sound_player()
        player.pcm.write = MagicMock()

        player.put("This is a buffer"*5)

        player.pcm.write.assert_called_with("This is a buffer"*5)