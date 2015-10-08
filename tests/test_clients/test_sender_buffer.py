import json
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
        sender2 = self.init_sender()

        def mock_get():
            if self.number_intervals < 5:
                self.number_intervals += 1
                return "Buffer", 100
            else:
                raise NotImplementedError

        sender.recorder.get = mock_get
        sender2.recorder.get = mock_get

        sender.initialize()
        sender2.initialize()

        self.assertNotEqual(sender.handler_port, sender2.handler_port)
        # Wait until buffer process has started!
        time.sleep(0.1)

        try:
            sender.main_loop()
        except NotImplementedError:
            # Is intended
            pass

        self.assertEqual(self.number_intervals, 5)
        self.assertEqual(len(self.send_buffer_list), 5)
        for buffer_item in self.send_buffer_list:
            self.assertEqual(buffer_item, "buffer=Buffer")

        try:
            sender2.main_loop()
        except NotImplementedError:
            # Is intended
            pass

        self.assertEqual(self.number_intervals, 5)
        self.assertEqual(len(self.send_buffer_list), 5)
        for buffer_item in self.send_buffer_list:
            self.assertEqual(buffer_item, "buffer=Buffer")

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        self.assertEqual(len(response_dict), 2)
        self.assertIn(sender.channel_hash, response_dict)
        self.assertIn(sender2.channel_hash, response_dict)

        sender.terminate()
        sender2.terminate()

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        self.assertEqual(len(response_dict), 0)




