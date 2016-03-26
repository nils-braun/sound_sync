from mock.mock import MagicMock

from sound_sync.audio.pcm.play import PCMPlay
from tests.fixtures import SoundTestCase


class TestPCMPlayer(SoundTestCase):
    def test_initialize(self):
        player = self.init_sound_player()

        self.alsaaudio.PCM.assert_called_with(device="default", type=self.PCM_PLAYBACK,
                                              mode=self.PCM_NONBLOCK)

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

        test_buffer = "This is a buffer"
        number_of_buffers = 5

        player = self.init_sound_player()
        pcm_response = [0, 0] +  [len(test_buffer) / 4] * number_of_buffers
        player.pcm.write = MagicMock(side_effect = pcm_response)

        player.put(test_buffer * number_of_buffers)
        send_buffers = player.pcm.write.call_args_list
        for i in range(0, 2):
            args, kwargs = send_buffers[i]
            self.assertEqual(len(args), 1)
            self.assertEqual(args[0], bytes(test_buffer * (number_of_buffers), encoding="utf8"))
            self.assertEqual(kwargs, {})

        for i in range(2, number_of_buffers):
            args, kwargs = send_buffers[i]
            self.assertEqual(len(args), 1)
            self.assertEqual(args[0], bytes(test_buffer * (number_of_buffers - i + 2), encoding="utf8"))
            self.assertEqual(kwargs, {})

    def test_put_with_errors(self):
        player = self.init_sound_player()

        self.counter = 0

        def player_mock(buffer):
            self.counter += 1
            if self.counter % 2 == 0:
                raise RuntimeError()
            else:
                return 2

        player.pcm.write = player_mock

        player.put("This is a test buffer")