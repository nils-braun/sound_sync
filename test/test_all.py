from unittest import TestCase

from test.test_mockingClient import MockingClient, MockingPCM
from server import RequestHandler
from clientListen import ClientListener
from clientSender import ClientSender
from informationBase import SocketBase


__author__ = "nilpferd"


class TestAllCases(TestCase):
    def initialize_all_sockets(self):
        self.mocking_client_sender = MockingClient()
        self.mocking_client_listener = MockingClient()
        self.mocking_client_server = MockingClient()
        self.mocking_client_server_2 = MockingClient()

        self.client_listener = ClientListener()
        self.client_sender = ClientSender()

        self.client_listener.client = self.mocking_client_listener
        self.client_sender.client = self.mocking_client_sender

    def start_server_listener(self, message):
        self.server_listener = RequestHandler(self.mocking_client_server, ("0.0.0.0", message), None)

    def start_server_listener_2(self, message):
        self.server_listener = RequestHandler(self.mocking_client_server_2, ("0.0.0.2", message), None)

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
        self.mocking_pcm_sender.sound_buffer_size = SocketBase.clientInformation.sound_buffer_size
        self.mocking_pcm_listener.sound_buffer_size = SocketBase.clientInformation.sound_buffer_size

        self.client_sender.pcm = self.mocking_pcm_sender
        self.client_listener.pcm = self.mocking_pcm_listener

        self.load_sound_buffers()

    def test_information_transport_sender_server(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()

        self.mocking_client_sender.add_out_message("ok")
        self.mocking_client_sender.add_out_message("ok")
        self.mocking_client_sender.add_out_message("ok")

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
        self.mocking_client_server.add_out_message(b"ok")
        self.mocking_client_server.add_out_message(b"ok")
        self.mocking_client_server.add_out_message(b"ok")
        self.mocking_client_server.add_out_message(b"ok")

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
        self.mocking_client_server.add_out_message(b"ok")
        self.mocking_client_server.add_out_message(b"ok")
        self.mocking_client_server.add_out_message(b"ok")
        self.mocking_client_server.add_out_message(b"ok")

        self.start_server_listener(self.test_information_transport_server_listener.__name__)

        self.assertEqual("ok", self.mocking_client_server.get_in_message())
        self.assertEqual(SocketBase.clientInformation.frame_rate, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(SocketBase.clientInformation.waiting_time, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(test_start_time, int(self.mocking_client_server.get_in_message()))
        self.assertTrue(self.server_listener.static_client_list.is_sender(True))

        RequestHandler.static_client_list.__init__()

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

    def test_buffer_transport_sender_server(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()

        self.mocking_client_sender.add_out_message("ok")
        self.mocking_client_sender.add_out_message("ok")
        self.mocking_client_sender.add_out_message("ok")

        # Test transport of sender
        self.client_sender.tell_server_sender_identity()
        self.client_sender.send_values_to_server()

        self.client_sender.collect_and_send_sound_data()

        self.assertEqual("sender", self.mocking_client_sender.get_in_message())
        self.assertEqual(SocketBase.clientInformation.frame_rate, int(self.mocking_client_sender.get_in_message()))
        self.assertEqual(SocketBase.clientInformation.waiting_time, int(self.mocking_client_sender.get_in_message()))

        self.assertEqual(SocketBase.clientInformation.sound_buffer_size,
                         len(self.mocking_client_sender.get_in_message()))

        self.assertRaises(IndexError, self.mocking_client_sender.get_in_message)

        # Test transport of server
        self.mocking_client_server.add_out_message(b"sender")
        self.mocking_client_server.add_out_message(SocketBase.clientInformation.frame_rate)
        self.mocking_client_server.add_out_message(SocketBase.clientInformation.waiting_time)

        test_buffer = bytes(bytearray(SocketBase.clientInformation.sound_buffer_size))

        for _ in xrange(2):
            self.mocking_client_server.add_out_message(test_buffer)

        SocketBase.clientInformation.frame_rate = 0
        SocketBase.clientInformation.waiting_time = 0
        SocketBase.clientInformation.sound_buffer_size = 0

        self.start_server_sender(self.test_buffer_transport_sender_server.__name__)

        self.assertEqual(2, len(RequestHandler.static_client_list.buffers))
        self.assertEqual(bytes(test_buffer),
                         bytes(RequestHandler.static_client_list.buffers[0]))
        self.assertEqual(0, RequestHandler.static_client_list.start_buffer_index)
        self.assertEqual(1, RequestHandler.static_client_list.end_buffer_index)

        RequestHandler.static_client_list.__init__()

    def test_buffer_transport_server_listener(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()
        RequestHandler.static_client_list.sender = True
        test_start_time = 736
        RequestHandler.static_client_list.start_time = test_start_time

        # Test transport of listener
        self.mocking_client_listener.add_out_message("ok")
        self.mocking_client_listener.add_out_message(SocketBase.clientInformation.frame_rate)
        self.mocking_client_listener.add_out_message(SocketBase.clientInformation.waiting_time)
        self.mocking_client_listener.add_out_message(test_start_time)
        test_buffer = bytes(bytearray(SocketBase.clientInformation.sound_buffer_size))

        for i in xrange(2):
            self.mocking_client_listener.add_out_message(10 + i)
            self.mocking_client_listener.add_out_message(test_buffer)

        self.client_listener.is_running = True
        self.client_listener.tell_server_receiver_identity()
        self.client_listener.get_audio_information()

        for i in xrange(2):
            self.client_listener.handle_new_message_loop()

        self.assertEqual(b"receiver", self.mocking_client_listener.get_in_message())
        self.assertEqual(2, len(self.client_listener.static_sound_buffer_list.buffers))
        self.assertEqual(test_buffer, self.client_listener.static_sound_buffer_list.get_buffer_by_buffer_index(10))
        self.assertEqual(10, self.client_listener.static_sound_buffer_list.start_buffer_index)
        self.assertEqual(11, self.client_listener.static_sound_buffer_list.end_buffer_index)

        for i in xrange(2):
            self.mocking_client_listener.add_out_message(12 + i)
            self.mocking_client_listener.add_out_message(test_buffer)

        self.client_listener.is_audio_playing = True
        self.client_listener.static_sound_buffer_list.current_buffer_index = 10

        for i in xrange(2):
            self.client_listener.handle_new_message_loop()

        RequestHandler.static_client_list.__init__()

        RequestHandler.static_client_list.sender = True
        RequestHandler.static_client_list.start_time = test_start_time

        self.assertEqual(4, len(self.client_listener.static_sound_buffer_list.buffers))
        self.assertEqual(test_buffer, self.client_listener.static_sound_buffer_list.get_buffer_by_buffer_index(12))
        self.assertEqual(10, self.client_listener.static_sound_buffer_list.start_buffer_index)
        self.assertEqual(13, self.client_listener.static_sound_buffer_list.end_buffer_index)
        self.assertEqual(12, self.client_listener.static_sound_buffer_list.current_buffer_index)
        self.assertEqual(2, len(self.mocking_pcm_listener.message_stack))
        self.assertEqual(test_buffer, self.mocking_pcm_listener.message_stack[0])

        # Test transport of server
        for i in xrange(100):
            RequestHandler.static_client_list.add_buffer(test_buffer)

        self.mocking_client_server.add_out_message(b"receiver")
        for _ in xrange(6):
            self.mocking_client_server.add_out_message("ok")

        self.start_server_listener(self.test_buffer_transport_server_listener.__name__)

        RequestHandler.static_client_list.__init__()

        self.assertEqual("ok", self.mocking_client_server.get_in_message())
        self.assertEqual(SocketBase.clientInformation.frame_rate, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(SocketBase.clientInformation.waiting_time, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(test_start_time, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(50, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(test_buffer, bytes(self.mocking_client_server.get_in_message()))
        self.assertEqual(51, int(self.mocking_client_server.get_in_message()))
        self.assertEqual(test_buffer, bytes(self.mocking_client_server.get_in_message()))

    def test_buffer_transport_server_listener_two_listener(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()

        RequestHandler.static_client_list.__init__()
        RequestHandler.static_client_list.sender = True
        test_start_time = 736
        RequestHandler.static_client_list.start_time = test_start_time

        for i in xrange(10):
            RequestHandler.static_client_list.add_buffer(i)

        self.mocking_client_server.add_out_message(b"receiver")
        self.mocking_client_server_2.add_out_message(b"receiver")

        for _ in xrange(6):
            self.mocking_client_server.add_out_message("ok")

        for _ in xrange(6):
            self.mocking_client_server_2.add_out_message("ok")

        self.start_server_listener(self.test_buffer_transport_server_listener_two_listener.__name__)
        self.start_server_listener_2(self.test_buffer_transport_server_listener_two_listener.__name__)

        RequestHandler.static_client_list.__init__()

        self.assertEqual(0, int(self.mocking_client_server.last_in_message[4]))
        self.assertEqual(0, int(self.mocking_client_server.last_in_message[5]))
        self.assertEqual(1, int(self.mocking_client_server.last_in_message[6]))
        self.assertEqual(1, int(self.mocking_client_server.last_in_message[7]))

        self.assertEqual(0, int(self.mocking_client_server_2.last_in_message[4]))
        self.assertEqual(0, int(self.mocking_client_server_2.last_in_message[5]))
        self.assertEqual(1, int(self.mocking_client_server_2.last_in_message[6]))
        self.assertEqual(1, int(self.mocking_client_server_2.last_in_message[7]))

    def test_buffer_transport_server_listener_two_listener_2(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()

        RequestHandler.static_client_list.__init__()
        RequestHandler.static_client_list.sender = True
        test_start_time = 736
        RequestHandler.static_client_list.start_time = test_start_time

        for i in xrange(100):
            RequestHandler.static_client_list.add_buffer(i)

        self.mocking_client_server.add_out_message(b"receiver")
        self.mocking_client_server_2.add_out_message(b"receiver")

        for _ in xrange(50):
            self.mocking_client_server.add_out_message("ok")

        for _ in xrange(6):
            self.mocking_client_server_2.add_out_message("ok")

        self.start_server_listener(self.test_buffer_transport_server_listener_two_listener_2.__name__)
        self.start_server_listener_2(self.test_buffer_transport_server_listener_two_listener_2.__name__)

        RequestHandler.static_client_list.__init__()

        self.assertEqual(50, int(self.mocking_client_server.last_in_message[4]))
        self.assertEqual(50, int(self.mocking_client_server.last_in_message[5]))
        self.assertEqual(51, int(self.mocking_client_server.last_in_message[6]))
        self.assertEqual(51, int(self.mocking_client_server.last_in_message[7]))

        self.assertEqual(50, int(self.mocking_client_server_2.last_in_message[4]))
        self.assertEqual(50, int(self.mocking_client_server_2.last_in_message[5]))
        self.assertEqual(51, int(self.mocking_client_server_2.last_in_message[6]))
        self.assertEqual(51, int(self.mocking_client_server_2.last_in_message[7]))

    def test_buffer_transport_server_listener_two_listener_3(self):
        self.initialize_all_sockets()
        self.initialize_all_sound_systems()

        RequestHandler.static_client_list.__init__()
        RequestHandler.static_client_list.sender = True
        test_start_time = 736
        RequestHandler.static_client_list.start_time = test_start_time

        for i in xrange(100):
            RequestHandler.static_client_list.add_buffer(i)

        self.mocking_client_server.add_out_message(b"receiver")
        self.mocking_client_server_2.add_out_message(b"receiver")

        for _ in xrange(6):
            self.mocking_client_server.add_out_message("ok")

        RequestHandler.static_client_list.add_listener(self.mocking_client_server)
        RequestHandler.static_client_list.listener_list[self.mocking_client_server] = 60

        self.start_server_listener(self.test_buffer_transport_server_listener_two_listener_3.__name__)

        RequestHandler.static_client_list.__init__()

        self.assertEqual(50, int(self.mocking_client_server.last_in_message[4]))
        self.assertEqual(50, int(self.mocking_client_server.last_in_message[5]))
        self.assertEqual(51, int(self.mocking_client_server.last_in_message[6]))
        self.assertEqual(51, int(self.mocking_client_server.last_in_message[7]))