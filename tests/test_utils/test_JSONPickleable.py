from unittest import TestCase
from sound_sync.entities.json_pickable import JSONPickleable


class Class():
    def __init__(self):
        self.a = None
        self.b = None
        self.c = None


class Encodable(JSONPickleable):
    def __init__(self):
        JSONPickleable.__init__(self)

        self.a = "Test"
        self.b = "Second Test"
        self._private = "Nothing"


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

    def test_do_not_fill_empty_objects(self):
        json_dict = {"a": "A", "b": "B", "d": "D"}
        JSONPickleable.fill_with_json(None, json_dict)

    def test_encode_json(self):
        test_object = Encodable()
        encoded_json = test_object.encode_json()

        self.assertEqual(encoded_json, {'a': 'Test', 'b': 'Second Test'})
