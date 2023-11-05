"""Unit tests for reporter.py file."""

import unittest

from gentoo_update import Reporter, generate_last_report


class TestGentooUpdate(unittest.TestCase):
    """Unit tests for the gentoo_update module."""

    def setUp(self):
        """Initialize test prerequisites."""
        report_for_tests = "logs_for_unit_tests"
        self.report_object = generate_last_report(report_for_tests, short_report=False)
        self.report = self.report_object.create_report()

    def test_report_object_type(self):
        """Test if the report_object is of type Reporter."""
        self.assertIs(type(self.report_object), Reporter)

    def test_report_status(self):
        """Test if the report status is SUCCESS."""
        status = self.report[1].split(" ")[-1]
        self.assertEqual(status, "SUCCESS")

    def test_report_packages(self):
        """Test if the report lists the expected packages."""
        packages = sum([pkg.split(" ", 1)[1:] for pkg in self.report[3:7]], [])
        correct_package_list = [
            "dev-libs/openssl 3.0.10:0/3->3.0.11:0/3",
            "net-fs/samba 4.18.4-r1->4.18.8",
            "net-libs/nghttp2 1.51.0:0/1.14->1.57.0:0/1.14",
            "www-client/firefox-bin 118.0.1:rapid->118.0.2:rapid",
        ]
        self.assertEqual(packages, correct_package_list)

    def test_disk_usage(self):
        """Test if the report shows the expected disk usage."""
        disk_usage = self.report[-4::]
        correct_disk_usage = [
            "Mount Point /",
            "Free Space 253G => 253G",
            "Used Space 177G => 177G",
            "Used (%) 42% => 42%",
        ]
        self.assertEqual(disk_usage, correct_disk_usage)


if __name__ == "__main__":
    unittest.main()
