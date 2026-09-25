import unittest
from e7wac.discovery import discover_assets, detect_cms

class TestDiscovery(unittest.TestCase):
    def test_base_href_resolution(self):
        # Without base href
        html_no_base = '<html><body><a href="en/generation/">Gen</a></body></html>'
        assets = discover_assets("https://example.com/some/path/", html_no_base, "full")
        self.assertIn(("https://example.com/some/path/en/generation/", "Link"), assets)
        
        # With base href
        html_base = '<html><head><base href="https://example.com/"></head><body><a href="en/generation/">Gen</a></body></html>'
        assets = discover_assets("https://example.com/some/path/", html_base, "full")
        self.assertIn(("https://example.com/en/generation/", "Link"), assets)
        
    def test_detect_cms(self):
        self.assertEqual(detect_cms('<meta name="generator" content="TYPO3 11">'), "TYPO3")
        self.assertEqual(detect_cms('<meta name="generator" content="WordPress 6.0">'), "WordPress")
        self.assertEqual(detect_cms('<html><body><script src="cdn.shopify.com/x.js"></script></body></html>'), "Shopify")
        self.assertEqual(detect_cms('<html><body>Nothing here</body></html>'), "Unknown")

if __name__ == '__main__':
    unittest.main()
