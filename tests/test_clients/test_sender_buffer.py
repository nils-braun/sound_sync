from unittest import TestCase
from sound_sync.clients.sender import Sender
from mock.mock import MagicMock, patch
from tests.test_server.server_test_case import ServerTestCase


class TestBufferSender(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        alsa_patcher = patch("sound_sync.audio.pcm.device.alsaaudio")
        alsaaudio = alsa_patcher.start()
        alsaaudio.cards = lambda: ["TestCard", "Loopback", "Bla"]

        self.number_intervals = 0
        self.addCleanup(alsa_patcher.stop)

        self.mocking_client = MagicMock()

        def fetch_mock(url, *args, **kwargs):
            self.assertTrue(url.startswith("http://ThisIsTheHost:16347"))
            url = url[len("http://ThisIsTheHost:16347"):]
            return self.fetch(url, *args, **kwargs)

        self.mocking_client.fetch = fetch_mock

        http_client_patcher = patch("sound_sync.clients.sender.httpclient")
        http_client = http_client_patcher.start()
        http_client.HTTPClient = lambda: self.mocking_client
        self.addCleanup(http_client_patcher.stop)

    def init_sender(self):
        sender = Sender()
        sender.host = "ThisIsTheHost"
        sender.manager_port = 16347
        sender.name = "TheName"
        sender.description = "TheDescription"
        return sender

    def test_buffer_sending(self):
        sender = self.init_sender()

        def mock_get():
            if self.number_intervals < 5:
                self.number_intervals += 1
                return ("Buffer", 100)
            else:
                raise AssertionError

        sender.recorder.get = mock_get

        sender.initialize()

        try:
            sender.main_loop()
        except AssertionError:
            # Is intended
            pass

        self.fail()



