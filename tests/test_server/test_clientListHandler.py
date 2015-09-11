import json
import urllib

from tests.test_server.server_test_case import ServerTestCase


class TestClientListFromServer(ServerTestCase):
    def test_get_clients(self):
        response = self.fetch('/clients/get')
        self.assertResponse(response, "{}")

    def test_set_clients_properties(self):
        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        parameters = {"name": "My New Name", "ip_address": "111.111.222.333"}
        body = urllib.urlencode(parameters)

        response = self.fetch('/clients/set/' + str(item_hash), method="POST", body=body)
        self.assertResponse(response, "")

        response = self.fetch('/clients/set/' + str(item_hash + "1"), method="POST", body=body)
        self.assertError(response, 502)

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        added_channel = response_dict[item_hash]

        self.assertEqual(added_channel["name"], "My New Name")
        self.assertEqual(added_channel["item_hash"], item_hash)
        self.assertEqual(added_channel["ip_address"], "111.111.222.333")

    def test_add_clients(self):
        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 1)

        added_client = response_dict[item_hash]

        self.assertEqual(type(added_client), dict)
        self.assertIn("login_time", added_client)
        self.assertIn("name", added_client)
        self.assertEqual(added_client["name"], "")

        self.assertIn("item_hash", added_client)
        self.assertEqual(added_client["item_hash"], item_hash)

        self.assertIn("ip_address", added_client)
        self.assertTrue(added_client["ip_address"].startswith("localhost"))

        self.assertEqual(len(added_client), 4)

        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertIn(item_hash, response_dict)
        self.assertEqual(len(response_dict), 2)

    def test_delete_clients(self):
        response = self.fetch('/clients/add')
        item_hash = self.assertResponse(response)

        response = self.fetch('/clients/delete/' + item_hash)
        self.assertResponse(response, "")

        response = self.fetch('/clients/get')
        response = self.assertResponse(response)
        response_dict = json.loads(response)

        self.assertEqual(len(response_dict), 0)

        response = self.fetch('/clients/delete/' + item_hash)
        self.assertError(response, 502)