from unittest import TestCase

from mock import MagicMock

from sound_sync.clients.base_listener import BaseListener
from sound_sync.clients.buffer_downloader_thread import BufferDownloaderThread
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import to_datetime, sleep
from tests.fixtures import ListenerTestCase, ServerTestCase


class TestBufferDownloaderThread(ListenerTestCase, ServerTestCase):
    def setUp(self):
        ListenerTestCase.setUp(self)
        ServerTestCase.setUp(self)

    def test_get_buffer_index_wrong(self):
        buffer_downloader = BufferDownloaderThread(None)

        self.assertRaises(AssertionError, buffer_downloader.get_buffer_index, "not start")

    def test_get_buffer_index(self):
        listener, connection, real_http_client = self.init_typical_setup()

        self.assertEqual(listener.downloader_thread.get_buffer_index("start"), 0)
        self.assertEqual(listener.downloader_thread.get_buffer_index("end"), 0)

        buffer = SoundBufferWithTime(bytes("Test", encoding="utf8"), 0, to_datetime("2010-01-01 01:01:00"))

        self.send_buffer(buffer.to_string(), listener, real_http_client)
        self.assertEqual(listener.downloader_thread.get_buffer_index("start"), 0)
        self.assertEqual(listener.downloader_thread.get_buffer_index("end"), 0)

        for i in range(100):
            self.send_buffer(buffer.to_string(), listener, real_http_client)

        self.assertEqual(listener.downloader_thread.get_buffer_index("start"), 1)
        self.assertEqual(listener.downloader_thread.get_buffer_index("end"), 100)

    def test_get_current_buffer_start_index(self):
        buffer_downloader = BufferDownloaderThread(None)

        buffer_downloader.get_buffer_index = MagicMock(return_value="Test")

        value = buffer_downloader.get_current_buffer_start_index()

        self.assertTrue(buffer_downloader.get_buffer_index.called_only_once_with("start"))
        self.assertEqual(value, "Test")

    def test_get_current_buffer_end_index(self):
        buffer_downloader = BufferDownloaderThread(None)

        buffer_downloader.get_buffer_index = MagicMock(return_value="Test")

        value = buffer_downloader.get_current_buffer_start_index()

        self.assertTrue(buffer_downloader.get_buffer_index.called_only_once_with("end"))
        self.assertEqual(value, "Test")

    def test_get_buffer(self):
        listener, connection, real_http_client = self.init_typical_setup()

        test_buffer = SoundBufferWithTime(bytes("Test", encoding="utf8"), 0, to_datetime("2010-01-01 01:01:00"))

        self.send_buffer(test_buffer.to_string(), listener, real_http_client)

        buffer_string = listener.downloader_thread.get_buffer(0)
        buffer = SoundBufferWithTime.construct_from_string(buffer_string)
        self.assertEqual(buffer, test_buffer)

        for i in range(150):
            test_buffer = SoundBufferWithTime(bytes("Test", encoding="utf8"), i + 1, to_datetime("2010-01-01 01:01:00"))
            self.send_buffer(test_buffer.to_string(), listener, real_http_client)

        buffer_string = listener.downloader_thread.get_buffer(150)
        buffer = SoundBufferWithTime.construct_from_string(buffer_string)
        self.assertEqual(buffer.buffer_number, 150)

        self.assertRaises(RuntimeError, listener.downloader_thread.get_buffer, 200)
        self.assertRaises(RuntimeError, listener.downloader_thread.get_buffer, 1)

    def test_run(self):
        listener = BaseListener()
        buffer_downloader = BufferDownloaderThread(listener)

        self.assertRaises(ValueError, buffer_downloader.run)

        listener, connection, real_http_client = self.init_typical_setup()

        for i in range(30):
            test_buffer = SoundBufferWithTime(bytes("Test", encoding="utf8"), i, to_datetime("2010-01-01 01:01:00"))
            self.send_buffer(test_buffer.to_string(), listener, real_http_client)

        listener.downloader_thread.start()

        sleep(0.6)

        listener.terminate()

        self.assertEqual(listener.buffer_list.get_start_index(), 0)
        self.assertEqual(listener.buffer_list.get_next_free_index(), 30)


