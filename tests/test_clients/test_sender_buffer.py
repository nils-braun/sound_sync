import time
from tornado import httpclient
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

        self.send_buffer_list = []

        def fetch_mock(url, *args, **kwargs):
            if url.startswith("http://ThisIsTheHost:16347"):
                url = url[len("http://ThisIsTheHost:16347"):]
                # noinspection PyArgumentList
                return self.fetch(url, *args, **kwargs)
            else:
                temp_client = httpclient.HTTPClient()
                # noinspection PyArgumentList
                self.send_buffer_list.append(kwargs["body"])
                return temp_client.fetch(url.replace("http://ThisIsTheHost:", "http://localhost:"), *args, **kwargs)

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
                return "Buffer", 100
            else:
                raise NotImplementedError

        sender.recorder.get = mock_get

        sender.initialize()
        # Wait until buffer process has started!
        time.sleep(0.1)

        try:
            sender.main_loop()
        except NotImplementedError:
            # Is intended
            pass

        self.assertEqual(self.number_intervals, 5)
        self.assertEqual(len(self.send_buffer_list), 5)
        self.assertEqual(self.send_buffer_list[0], "buffer=Buffer")
        self.assertEqual(self.send_buffer_list[1], "buffer=Buffer")
        self.assertEqual(self.send_buffer_list[2], "buffer=Buffer")
        self.assertEqual(self.send_buffer_list[3], "buffer=Buffer")
        self.assertEqual(self.send_buffer_list[4], "buffer=Buffer")



