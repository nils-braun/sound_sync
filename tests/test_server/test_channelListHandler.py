import json
import socket
import urllib

from mock import patch

from sound_sync.timing.time_utils import to_datetime
from tests.fixtures import LowLevelServerTestCase


class TestChannelListFromServer(LowLevelServerTestCase):
    def test_get_channels(self):
        response = self.get_channels_html()
        self.assertResponse(response, "{}")

    def test_set_channel_properties(self):
        response = self.add_channel_html()
        item_hash = self.assertResponse(response)

        test_name = "My New Name"
        test_description = "This is a description. It <strong>even</strong> have some html tags."
        parameters = {"name": test_name, "description": test_description}
        body = urllib.parse.urlencode(parameters)

        response = self.set_channel_html(body, item_hash)
        self.assertResponse(response, "")

        response = self.set_channel_html(body, item_hash + "1")
        self.assertError(response, 502)

        response = self.get_channels_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        added_channel = response_dict[item_hash]

        self.assertEqual(added_channel["name"], test_name)
        self.assertEqual(added_channel["channel_hash"], item_hash)
        self.assertEqual(added_channel["description"], test_description)

    @patch("sound_sync.timing.time_utils.datetime")
    def test_add_channels(self, time_mock):

        import datetime
        time_mock.datetime.utcnow = lambda: datetime.datetime(1, 2, 3, 4, 5)
        time_mock.datetime.strptime = datetime.datetime.strptime

        response = self.add_channel_html()
        item_hash = self.assertResponse(response)

        response = self.get_channels_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 1)

        added_channel = response_dict[item_hash]

        self.assertEqual(type(added_channel), dict)

        self.assertIn("start_time", added_channel)
        self.assertEqual(to_datetime(added_channel["start_time"]), datetime.datetime(1, 2, 3, 4, 5))

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

        self.assertIn("buffer_size", added_channel)
        self.assertEqual(int(added_channel["buffer_size"]), 1024)

        self.assertIn("added_delay", added_channel)
        self.assertEqual(float(added_channel["added_delay"]), 0.0)

        self.assertIn("factor", added_channel)
        self.assertEqual(float(added_channel["factor"]), 10)

        self.assertIn("handler_port", added_channel)
        self.assertEqual(len(added_channel), 11)

        response = self.add_channel_html()
        item_hash = self.assertResponse(response)

        response = self.get_channels_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 2)

    def test_delete_channels(self):
        response = self.add_channel_html()
        item_hash = self.assertResponse(response)

        response = self.delete_channel_html(item_hash)
        self.assertResponse(response, "")

        response = self.get_channels_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertEqual(len(response_dict), 0)

        response = self.delete_channel_html(item_hash)
        self.assertError(response, 502)