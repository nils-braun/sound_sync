from unittest import TestCase
from test.test_mockingClient import MockingClient, MockingPCM
from server import RequestHandler
from clientListener import ClientListener
from clientSender import ClientSender


__author__ = "nils"

class TestAllCases(TestCase):
  # TODO Test the buffer size of all components
  def initialize_all_sockets(self):
    self.mocking_client_sender = MockingClient()
    self.mocking_client_listener = MockingClient()
    self.mocking_client_server = MockingClient()
    
    self.client_listener = ClientListener()
    self.client_sender = ClientSender()
    self.server_listener = RequestHandler(self.mocking_client_listener, ("0.0.0.0", "0"), self.mocking_client_server)
    self.server_sender = RequestHandler(self.mocking_client_sender, ("0.0.0.0", "0"), self.mocking_client_server)

    self.client_listener.client = self.mocking_client_listener
    self.client_sender.client = self.mocking_client_sender

   
  def initialize_all_sound_systems(self):
    SocketBase.waiting_time = 836
    SocketBase.frame_rate = 737
    SocketBase.multiple_frame_buffer = 2
    self.mocking_pcm_sender = MockingPCM()
    self.mocking_pcm_listener = MockingPCM()

    # Load buffers accordingly! With the correct buffer size! Look it up in the corresponding test with real pcm device!
    self.fail()
  
  
  def test_information_transport(self):
    self.initialize_all_sockets()
    
    # Implement startup of clients
    self.client_sender.tell_server_sender_identity()
    self.client_sender.send_values_to_server()
    # Implement information processing
    # Implement test for correct buffer_size

    self.fail()
