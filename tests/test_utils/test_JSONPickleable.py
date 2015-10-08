from unittest import TestCase
from sound_sync.rest_server.server_items.json_pickable import JSONPickleable


class Class():
  def __init__(self):
    self.a = None
    self.b = None
    self.c = None


class TestJSONPickleable(TestCase):
    def test_fill_with_json(self):

        json_dict = {"a": "A", "b": "B", "d": "D"}
        test_object = Class()

        self.assertEqual(test_object.a, None)
        self.assertEqual(test_object.b, None)
        self.assertEqual(test_object.c, None)

        JSONPickleable.fill_with_json(test_object, json_dict)

        self.assertEqual(test_object.a, "A")
        self.assertEqual(test_object.b, "B")
        self.assertEqual(test_object.c, None)
