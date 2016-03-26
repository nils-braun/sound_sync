import json
import urllib

from tests.fixtures import ServerTestCase


class TestClientListFromServer(ServerTestCase):
    def test_get_clients(self):
        response = self.get_clients_html()
        self.assertResponse(response, "{}")

    def test_set_clients_properties(self):
        response = self.add_client_html()
        item_hash = self.assertResponse(response)

        test_name = "My New Name"
        test_ip_address = "111.111.222.333"
        parameters = {"name": test_name, "ip_address": test_ip_address}
        body = urllib.parse.urlencode(parameters)

        response = self.set_client_html(body, item_hash)
        self.assertResponse(response, "")

        response = self.set_client_html(body, item_hash + "1")
        self.assertError(response, 502)

        response = self.get_clients_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        added_channel = response_dict[item_hash]

        self.assertEqual(added_channel["name"], test_name)
        self.assertEqual(added_channel["client_hash"], item_hash)
        self.assertEqual(added_channel["ip_address"], test_ip_address)

    def test_add_clients(self):
        response = self.add_client_html()
        item_hash = self.assertResponse(response)

        response = self.get_clients_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 1)

        added_client = response_dict[item_hash]

        self.assertEqual(type(added_client), dict)
        self.assertIn("login_time", added_client)
        self.assertIn("name", added_client)
        self.assertEqual(added_client["name"], "")

        self.assertIn("client_hash", added_client)
        self.assertEqual(added_client["client_hash"], item_hash)

        self.assertIn("ip_address", added_client)
        self.assertTrue(added_client["ip_address"].startswith("localhost"))

        self.assertEqual(len(added_client), 4)

        response = self.add_client_html()
        item_hash = self.assertResponse(response)

        response = self.get_clients_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 2)

    def test_delete_clients(self):
        response = self.add_client_html()
        item_hash = self.assertResponse(response)

        response = self.delete_client_html(item_hash)
        self.assertResponse(response, "")

        response = self.get_clients_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertEqual(len(response_dict), 0)

        response = self.delete_client_html(item_hash)
        self.assertError(response, 502)

