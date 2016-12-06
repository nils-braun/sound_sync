from sound_sync.clients.base_listener import BaseListener
from sound_sync.clients.buffer_downloader_thread import BufferDownloaderThread
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import to_datetime, sleep
from tests.fixtures import ListenerTestCase, ServerTestCase


class TestBufferDownloaderThread(ListenerTestCase, ServerTestCase):
    def setUp(self):
        ListenerTestCase.setUp(self)
        ServerTestCase.setUp(self)

    def test_run(self):
        listener = BaseListener()
        buffer_downloader = BufferDownloaderThread(listener)

        self.assertRaises(ValueError, buffer_downloader.run)

        listener = self.init_typical_setup()

        for i in range(40):
            test_buffer = SoundBufferWithTime(bytes("Test", encoding="utf8"), i, to_datetime("2010-01-01 01:01:00"))
            self.connection.add_buffer(test_buffer, listener.channel_hash)

        listener.downloader_thread.run(testing_mode=True)

        listener.terminate()

        self.assertEqual(listener.buffer_list.get_start_index(), 10)

        for i in range(10, 40):
            test_buffer = SoundBufferWithTime(bytes("Test", encoding="utf8"), i, to_datetime("2010-01-01 01:01:00"))
            result_buffer = SoundBufferWithTime.construct_from_string(listener.buffer_list.get_buffer(str(i)))

            self.assertEqual(test_buffer.buffer_number, result_buffer.buffer_number)

        self.assertEqual(listener.buffer_list.get_next_free_index(), 40)


