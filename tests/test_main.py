import unittest

from hr_bridge_pico.__main__ import build_parser


class ParserTest(unittest.TestCase):
    def test_defaults(self):
        args = build_parser().parse_args([])
        self.assertEqual(args.url, "http://127.0.0.1:8080")
        self.assertIsNone(args.port)
        self.assertFalse(args.quiet)

    def test_overrides(self):
        args = build_parser().parse_args(["--url", "http://127.0.0.1:9999", "--port", "COM7", "--quiet"])
        self.assertEqual(args.url, "http://127.0.0.1:9999")
        self.assertEqual(args.port, "COM7")
        self.assertTrue(args.quiet)


if __name__ == "__main__":
    unittest.main()
