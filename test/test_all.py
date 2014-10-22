from unittest import TestCase

from test.test_mockingClient import MockingClient, MockingPCM
from server import RequestHandler
from clientListen import ClientListener
from clientSender import ClientSender
from informationBase import SocketBase


__author__ = "nils"


class TestAllCases(TestCase):
    # TODO Test the buffer size of all components
    def initialize_all_sockets(self):
        self.mocking_client_sender = MockingClient()
        self.mocking_client_listener = MockingClient()
        self.mocking_client_server = MockingClient()

        self.client_listener = ClientListener()
        self.client_sender = ClientSender()

        self.client_listener.client = self.mocking_client_listener
        self.client_sender.client = self.mocking_client_sender

    def start_server_listener(self, message):
        self.server_listener = RequestHandler(self.mocking_client_server, ("0.0.0.0", message), None)

    def start_server_sender(self, message):
        self.server_sender = RequestHandler(self.mocking_client_server, ("0.0.0.0", message), None)

    def load_sound_buffers(self):
        test_buffer = bytes(bytearray(SocketBase.clientInformation.sound_buffer_size /
                                      SocketBase.clientInformation.multiple_buffer_factor))
        for _ in xrange(SocketBase.clientInformation.multiple_buffer_factor):
            self.mocking_pcm_sender.add_buffer(test_buffer)

    def initialize_all_sound_systems(self):
        SocketBase.clientInformation.waiting_time = 836
        SocketBase.clientInformation.frame_rate = 737
        SocketBase.clientInformation.multiple_frame_buffer = 2
        SocketBase.clientInformation.set_sound_buffer_size()
        self.mocking_pcm_sender = MockingPCM()
        self.mocking_pcm_listener = MockingPCM()

        self.load_sound_buffers()

    def test_information_transport_sender_server(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()

        # Test transport of sender
        self.client_sender.tell_server_sender_identity()
        self.client_sender.send_values_to_server()

        self.assertEqual("sender", self.mocking_client_sender.get_in_message())
        self.assertEqual(SocketBase.clientInformation.frame_rate, int(self.mocking_client_sender.get_in_message()))
        self.assertEqual(SocketBase.clientInformation.waiting_time, int(self.mocking_client_sender.get_in_message()))

        # Test transport of server
        tmp_frame_rate = SocketBase.clientInformation.frame_rate
        tmp_waiting_time = SocketBase.clientInformation.waiting_time
        tmp_sound_buffer_size = SocketBase.clientInformation.sound_buffer_size

        self.mocking_client_server.add_out_message(b"sender")
        self.mocking_client_server.add_out_message(SocketBase.clientInformation.frame_rate)
        self.mocking_client_server.add_out_message(SocketBase.clientInformation.waiting_time)

        SocketBase.clientInformation.frame_rate = 0
        SocketBase.clientInformation.waiting_time = 0
        SocketBase.clientInformation.sound_buffer_size = 0

        self.start_server_sender(self.test_information_transport_sender_server.__name__)

        self.assertEqual(tmp_frame_rate, SocketBase.clientInformation.frame_rate)
        self.assertEqual(tmp_waiting_time, SocketBase.clientInformation.waiting_time)
        self.assertEqual(tmp_sound_buffer_size, SocketBase.clientInformation.sound_buffer_size)

    def test_information_transport_server_listener_no_server(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()
        self.mocking_client_server.add_out_message(b"receiver")

        self.start_server_listener(self.test_information_transport_server_listener_no_server.__name__)

        self.assertTrue(self.mocking_client_server.closed)

    def test_information_transport_server_listener(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()
        # Add a sender temporally
        RequestHandler.static_client_list.sender = True
        test_start_time = 736
        RequestHandler.static_client_list.start_time = test_start_time

        # Test transport of server
        self.mocking_client_server.add_out_message(b"receiver")

        self.start_server_listener(self.test_information_transport_server_listener.__name__)

        self.assertEqual("ok", self.mocking_client_server.get_in_message())
        self.assertEqual(SocketBase.clientInformation.frame_rate, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(SocketBase.clientInformation.waiting_time, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(test_start_time, int(self.mocking_client_server.get_in_message()))

        RequestHandler.static_client_list.sender = 0
        RequestHandler.static_client_list.start_time = 0

        # Test transport of listener
        tmp_frame_rate = SocketBase.clientInformation.frame_rate
        tmp_waiting_time = SocketBase.clientInformation.waiting_time
        tmp_sound_buffer_size = SocketBase.clientInformation.sound_buffer_size

        self.mocking_client_listener.add_out_message("ok")
        self.mocking_client_listener.add_out_message(SocketBase.clientInformation.frame_rate)
        self.mocking_client_listener.add_out_message(SocketBase.clientInformation.waiting_time)
        self.mocking_client_listener.add_out_message(test_start_time)

        SocketBase.clientInformation.frame_rate = 0
        SocketBase.clientInformation.waiting_time = 0
        SocketBase.clientInformation.sound_buffer_size = 0

        self.client_listener.tell_server_receiver_identity()
        self.client_listener.get_audio_information()

        self.assertEqual(b"receiver", self.mocking_client_listener.get_in_message())

        self.assertEqual(tmp_frame_rate, SocketBase.clientInformation.frame_rate)
        self.assertEqual(tmp_waiting_time, SocketBase.clientInformation.waiting_time)
        self.assertEqual(tmp_sound_buffer_size, SocketBase.clientInformation.sound_buffer_size)

