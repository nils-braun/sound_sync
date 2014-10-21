from unittest import TestCase

__author__ = 'nils'

from informationBase import ClientInformationBase


class TestClientInformationBase(TestCase):
    def test_set_sound_buffer_size(self):
        client_information = ClientInformationBase()
        client_information.frame_rate = 100340435
        client_information.waiting_time = 2395945
        client_information.set_sound_buffer_size()
        self.assertEqual(int(4 * client_information.waiting_time / 1000.0 * client_information.frame_rate),
                         client_information.sound_buffer_size)