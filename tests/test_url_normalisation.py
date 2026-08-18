import unittest
from e7wac.discovery import clean_url
from e7wac.http import is_same_domain

class TestUrlNormalization(unittest.TestCase):
    def test_clean_url(self):
        self.assertEqual(clean_url("http://Example.com/Path#hash"), "http://example.com/Path")
        self.assertEqual(clean_url("https://example.com"), "https://example.com/")
        
    def test_is_same_domain(self):
        self.assertTrue(is_same_domain("https://example.com/foo", "example.com"))
        self.assertFalse(is_same_domain("https://external.com/foo", "example.com"))

if __name__ == '__main__':
    unittest.main()
