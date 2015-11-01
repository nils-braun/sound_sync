from unittest import TestCase
from sound_sync.audio.sound_device import SoundDevice
from sound_sync.clients.sender import Sender
from mock.mock import MagicMock, patch


class TestSender(TestCase):
    def init_sender(self):
        sender = Sender()
        sender.connection.host = "ThisIsTheHost"
        sender.connection.manager_port = 16347
        sender.name = "TheName"
        sender.description = "TheDescription"
        return sender

    def test_manager_string(self):
        sender = self.init_sender()
        self.assertEqual(sender.connection.manager_string, "http://ThisIsTheHost:16347")

    def test_handler_string(self):
        sender = Sender()
        sender.connection.host = "ThisIsTheHost"
        self.assertRaises(ValueError, getattr, sender, "handler_string")

        sender.handler_port = 7589
        self.assertEqual(sender.handler_string, "http://ThisIsTheHost:7589")

    def test_remove_channel_from_server(self):
        sender = self.init_sender()
        sender.channel_hash = "12345"

        sender.connection.http_client = MagicMock()

        sender.connection.remove_channel_from_server(sender.channel_hash)
        # noinspection PyUnresolvedReferences
        sender.connection.http_client.fetch.assert_called_with("http://ThisIsTheHost:16347/channels/delete/12345")

    @patch("sound_sync.clients.connection.httpclient")
    def test_terminate(self, http_client_patch):
        http_client_patch.HTTPClient = lambda: 4734
        http_client_patch.HTTPError = AssertionError

        sender = self.init_sender()
        sender.connection.remove_channel_from_server = MagicMock()

        try:
            sender.terminate()
        except:
            self.fail()

        sender.channel_hash = "896"
        sender.connection.remove_channel_from_server = MagicMock()

        sender.terminate()
        # noinspection PyUnresolvedReferences
        sender.connection.remove_channel_from_server.assert_called_with("896")

    @patch("sound_sync.clients.connection.httpclient")
    def test_initialize(self, http_client_patch):

        class MockResponse:
            def __init__(self, body):
                self.body = body

        class MockClient:
            def __init__(self):
                pass

            @staticmethod
            def fetch(url, body=None, method=None):
                if url == "http://ThisIsTheHost:16347/channels/add":
                    return MockResponse("8456")

                elif url == "http://ThisIsTheHost:16347/channels/get":
                    return MockResponse("""
                                        {"8456":
                                            {"name": "",
                                             "channel_hash": "8456",
                                             "description": "",
                                             "now_playing": "",
                                             "channels": "2",
                                             "added_delay": "0",
                                             "frame_rate": "44100",
                                             "factor": "10",
                                             "buffer_size": "1024",
                                             "handler_port": "237",
                                             "waiting_time": "10"}
                                        }""")

                elif url == "http://ThisIsTheHost:16347/channels/set/8456" and method == "POST":
                    assert body == "name=TheName&description=TheDescription"

                else:
                    raise AssertionError

        http_client_patch.HTTPClient = MockClient
        sender = self.init_sender()
        sender.recorder = SoundDevice()
        sender.recorder.initialize = MagicMock()

        sender.initialize()
        # noinspection PyUnresolvedReferences
        sender.recorder.initialize.assert_called_with()

        self.assertEqual(int(sender.recorder.buffer_size), 1024)
        self.assertEqual(int(sender.recorder.frame_rate), 44100)
        self.assertEqual(int(sender.recorder.channels), 2)
        self.assertEqual(int(sender.recorder.factor), 10)
        self.assertEqual(int(sender.handler_port), 237)

    def test_initialize_twice(self):
        sender = self.init_sender()

        sender.channel_hash = "8364"
        sender.initialize()

    @patch("sound_sync.clients.connection.httpclient")
    def test_main_loop(self, http_client_patch):
        mocking_client = MagicMock()
        http_client_patch.HTTPClient = lambda: mocking_client

        sender = self.init_sender()

        self.assertRaises(AssertionError, sender.main_loop)

        sender.channel_hash = "345"
        sender.handler_port = 547647

        self.number_intervals = 0

        def mock_get():
            if self.number_intervals < 5:
                self.number_intervals += 1
                return "Buffer", 100
            else:
                raise NotImplementedError

        sender.recorder.get = mock_get


        try:
            sender.main_loop()
        except NotImplementedError:
            # This is intended
            pass

        mocking_client.fetch.assert_called_with('http://ThisIsTheHost:547647/add',
                                                method="POST", body="buffer=Buffer")

