from unittest import TestCase
from sound_sync.audio.sound_device import SoundDevice
from sound_sync.clients.listener import Listener
from mock.mock import MagicMock, patch


class TestListener(TestCase):
    def init_listener(self):
        listener = Listener()
        listener.host = "ThisIsTheHost"
        listener.manager_port = 16347
        listener.name = "TheName"
        listener.description = "TheDescription"
        return listener

    def test_manager_string(self):
        listener = self.init_listener()
        self.assertEqual(listener.manager_string, "http://ThisIsTheHost:16347")

    def test_handler_string(self):
        listener = Listener()
        listener.host = "ThisIsTheHost"
        self.assertRaises(ValueError, getattr, listener, "handler_string")

        listener._connected_channel = MagicMock()
        listener._connected_channel.handler_port = 7589

        self.assertEqual(listener.handler_string, "http://ThisIsTheHost:7589")

    def test_remove_listener_from_server(self):
        listener = self.init_listener()
        listener.client_hash = "12345"

        listener.http_client = MagicMock()

        listener.remove_client_from_server(listener.client_hash)
        # noinspection PyUnresolvedReferences
        listener.http_client.fetch.assert_called_with("http://ThisIsTheHost:16347/clients/delete/12345")

    @patch("sound_sync.clients.base.httpclient")
    def test_terminate(self, http_client_patch):
        http_client_patch.HTTPClient = lambda: 4734
        http_client_patch.HTTPError = AssertionError

        listener = self.init_listener()
        listener.remove_client_from_server = MagicMock()

        try:
            listener.terminate()
        except:
            self.fail()

        listener.client_hash = "896"
        listener.remove_client_from_server = MagicMock()

        listener.terminate()
        # noinspection PyUnresolvedReferences
        listener.remove_client_from_server.assert_called_with("896")

    @patch("sound_sync.clients.base.httpclient")
    def test_initialize(self, http_client_patch):

        class MockResponse:
            def __init__(self, body):
                self.body = body

        class MockClient:
            added = False
            settings_received = False
            settings_set = False

            def __init__(self):
                pass

            @staticmethod
            def fetch(url, body=None, method=None):
                if url == "http://ThisIsTheHost:16347/clients/add":
                    MockClient.added = True
                    return MockResponse("8456")

                elif url == "http://ThisIsTheHost:16347/channels/get":
                    MockClient.settings_received = True
                    return MockResponse("""
                                        {"1154":
                                            {"name": "",
                                             "channel_hash": "1154",
                                             "start_time": "2015-08-24 22:23:49.928645",
                                             "description": "DESCRIPTION",
                                             "now_playing": "NOW:PLAYING",
                                             "full_buffer_size": "11",
                                             "channels": "2",
                                             "added_delay": "0",
                                             "frame_rate": "44100",
                                             "factor": "10",
                                             "buffer_size": "1024",
                                             "handler_port": "237",
                                             "waiting_time": "10"}
                                        }""")

                elif url == "http://ThisIsTheHost:16347/clients/set/8456" and method == "POST":
                    MockClient.settings_set = True
                    assert body == "name=TheName"

                else:
                    raise AssertionError

        http_client_patch.HTTPClient = MockClient
        listener = self.init_listener()
        listener.channel_hash = "1154"
        listener.player = SoundDevice()
        listener.player.initialize = MagicMock()

        listener.initialize()
        # noinspection PyUnresolvedReferences
        listener.player.initialize.assert_called_with()

        self.assertTrue(http_client_patch.HTTPClient.added)
        self.assertTrue(http_client_patch.HTTPClient.settings_received)
        self.assertTrue(http_client_patch.HTTPClient.settings_set)

        self.assertEqual(int(listener.player.buffer_size), 1024)
        self.assertEqual(int(listener.player.frame_rate), 44100)
        self.assertEqual(int(listener.player.channels), 2)
        self.assertEqual(int(listener.player.factor), 10)
        self.assertEqual(int(listener.player.waiting_time), 10)
        self.assertEqual(listener.player.start_time, "2015-08-24 22:23:49.928645")

        self.assertEqual(int(listener._connected_channel.handler_port), 237)
        self.assertEqual(listener._connected_channel.channel_hash, "1154")
        self.assertEqual(listener._connected_channel.description, "DESCRIPTION")
        self.assertEqual(listener._connected_channel.now_playing, "NOW:PLAYING")
        self.assertEqual(int(listener._connected_channel.full_buffer_size), 11)

    def test_initialize_twice(self):
        listener = self.init_listener()

        listener.client_hash = "8364"
        listener.initialize()

    @patch("sound_sync.clients.base.httpclient")
    def test_main_loop(self, http_client_patch):
         mocking_client = MagicMock()
         http_client_patch.HTTPClient = lambda: mocking_client

         listener = self.init_listener()

         self.assertRaises(AssertionError, listener.main_loop)
    #
    #     sender.channel_hash = "345"
    #     sender.handler_port = 547647
    #
    #     self.number_intervals = 0
    #
    #     def mock_get():
    #         if self.number_intervals < 5:
    #             self.number_intervals += 1
    #             return "Buffer", 100
    #         else:
    #             raise NotImplementedError
    #
    #     sender.recorder.get = mock_get
    #
    #
    #     try:
    #         sender.main_loop()
    #     except NotImplementedError:
    #         # This is intended
    #         pass
    #
    #     mocking_client.fetch.assert_called_with('http://ThisIsTheHost:547647/add',
    #                                             method="POST", body="buffer=Buffer")

