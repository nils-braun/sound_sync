import json
import socket
import urllib

from tests.test_server.server_test_case import ServerTestCase


class TestChannelListFromServer(ServerTestCase):
    def test_get_channels(self):
        response = self.fetch('/channels/get')
        self.assertResponse(response, "{}")

    def test_set_channel_properties(self):
        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        parameters = {"name": "My New Name", "description": "This is a description. It <strong>even</strong>" +
                                                            "have some html tags."}
        body = urllib.urlencode(parameters)

        response = self.fetch('/channels/set/' + str(item_hash), method="POST", body=body)
        self.assertResponse(response, "")

        response = self.fetch('/channels/set/' + str(item_hash + "1"), method="POST", body=body)
        self.assertError(response, 502)

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        added_channel = response_dict[item_hash]

        self.assertEqual(added_channel["name"], "My New Name")
        self.assertEqual(added_channel["channel_hash"], item_hash)
        self.assertEqual(added_channel["description"], "This is a description. It <strong>even</strong>" +
                         "have some html tags.")

    def test_add_channels(self):
        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 1)

        added_channel = response_dict[item_hash]

        self.assertEqual(type(added_channel), dict)
        self.assertIn("start_time", added_channel)

        self.assertIn("name", added_channel)
        self.assertEqual(added_channel["name"], "")

        self.assertIn("channel_hash", added_channel)
        self.assertEqual(added_channel["channel_hash"], item_hash)

        self.assertIn("description", added_channel)
        self.assertEqual(added_channel["description"], "")

        self.assertIn("now_playing", added_channel)
        self.assertEqual(added_channel["now_playing"], "")

        self.assertIn("channels", added_channel)
        self.assertEqual(int(added_channel["channels"]), 2)

        self.assertIn("frame_rate", added_channel)
        self.assertEqual(int(added_channel["frame_rate"]), 44100)

        self.assertIn("waiting_time", added_channel)
        self.assertEqual(int(added_channel["waiting_time"]), 10)

        self.assertIn("buffer_size", added_channel)
        self.assertEqual(int(added_channel["buffer_size"]), 1024)

        self.assertIn("added_delay", added_channel)
        self.assertEqual(float(added_channel["added_delay"]), 0.0)

        self.assertIn("factor", added_channel)
        self.assertEqual(float(added_channel["factor"]), 10)

        self.assertIn("handler_port", added_channel)

        self.assertIn("full_buffer_size", added_channel)
        self.assertEqual(float(added_channel["full_buffer_size"]), 10)

        # Test if the handler_port is really free
        s = socket.socket()
        try:
            s.bind(("", int(added_channel["handler_port"])))
        except socket.error:
            self.fail()

        self.assertEqual(len(added_channel), 13)

        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 2)

    def test_delete_channels(self):
        response = self.fetch('/channels/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/channels/delete/' + item_hash)
        self.assertResponse(response, "")

        response = self.fetch('/channels/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertEqual(len(response_dict), 0)

        response = self.fetch('/channels/delete/' + item_hash)
        self.assertError(response, 502)