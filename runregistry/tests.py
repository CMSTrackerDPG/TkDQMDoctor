import unittest

from runregistry.utilities import (
    transform_lowstat_to_boolean,
    list_as_comma_separated_string,
    list_to_dict,
)


class TestUtilities(unittest.TestCase):
    def test_transform_lowstat_to_boolean(self):
        run_dict = {
            "pixel_lowstat": "LOW_STATS",
            "sistrip_lowstat": "Bla",
            "tracking_lowstat": "LOW_STATS",
        }

        transform_lowstat_to_boolean([run_dict])

        self.assertTrue(run_dict["pixel_lowstat"])
        self.assertFalse(run_dict["sistrip_lowstat"])
        self.assertTrue(run_dict["tracking_lowstat"])

        run_dict = {
            "pixel_lowstat": 123,
            "sistrip_lowstat": "LOW_STATS",
            "tracking_lowstat": None,
        }

        transform_lowstat_to_boolean([run_dict])

        self.assertFalse(run_dict["pixel_lowstat"])
        self.assertTrue(run_dict["sistrip_lowstat"])
        self.assertFalse(run_dict["tracking_lowstat"])

    def test_list_as_comma_separated_string(self):
        run_list = ["123", 4234, "-1"]
        run_list_string = list_as_comma_separated_string(run_list)
        self.assertEqual("'123', '4234', '-1'", run_list_string)

    def test_list_to_dict(self):
        list_of_lists = [["a", "b", "c"], [None, 999, "f"], [-1, "h", "i"]]
        keys = ["x", "y", "z"]

        list_of_dicts = list_to_dict(list_of_lists, keys)

        expected_dict_list = [
            {"x": "a", "y": "b", "z": "c"},
            {"x": None, "y": 999, "z": "f"},
            {"x": -1, "y": "h", "z": "i"},
        ]

        self.assertEqual(expected_dict_list, list_of_dicts)
