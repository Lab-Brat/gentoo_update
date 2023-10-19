import unittest

from gentoo_update import Reporter, generate_last_report


class TestGentooUpdate(unittest.TestCase):
    def setUp(self):
        report_for_tests = "logs_for_unit_tests"
        self.report = generate_last_report(report_for_tests, short_report=False)

    def test_report_object_type(self):
        self.assertIs(type(self.report), Reporter)


if __name__ == "__main__":
    unittest.main()
