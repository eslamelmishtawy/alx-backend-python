#!/usr/bin/env python3
"""Unit tests for utils: access_nested_map, get_json, and memoize."""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for utils.access_nested_map."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Return the nested value for a valid path."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, missing_key):
        """Raise KeyError whose message is the missing key."""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{missing_key}'")


class TestGetJson(unittest.TestCase):
    """Tests for utils.get_json."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Call requests.get once and return response.json()."""
        with patch("utils.requests.get") as mock_get:
            resp = Mock()
            resp.json.return_value = test_payload
            mock_get.return_value = resp

            result = get_json(test_url)

            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Tests for utils.memoize decorator."""

    def test_memoize(self):
        """Cache property so the underlying method is called only once."""

        class TestClass:
            """Fixture class for memoize behavior."""

            def a_method(self):
                """Return a constant used to verify memoization."""
                return 42

            @memoize
            def a_property(self):
                """Return a_method value via memoized property."""
                return self.a_method()

        with patch.object(TestClass, "a_method", return_value=42) as mock_m:
            obj = TestClass()
            self.assertEqual(obj.a_property, 42)
            self.assertEqual(obj.a_property, 42)
            mock_m.assert_called_once()


if __name__ == "__main__":
    unittest.main()
