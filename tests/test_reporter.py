"""Unit tests for reporter.py file."""

import unittest
from os import path

from gentoo_update.gentoo_update import (
    generate_report,
    get_available_log_files,
)
from gentoo_update.reporter import Reporter
from _report_packages_2 import report_2_packages


class TestGentooUpdate(unittest.TestCase):
    """Unit tests for the gentoo_update module."""

    def setUp(self):
        """Initialize test prerequisites."""
        test_reporter_path = path.dirname(path.abspath(__file__))
        logs_for_tests = f"{test_reporter_path}/logs_for_unit_tests"
        log_1, log_2 = get_available_log_files(logs_for_tests, 2)

        self.report_object_1 = generate_report(logs_for_tests, log_1)
        self.report_object_2 = generate_report(logs_for_tests, log_2)
        self.report_1 = self.report_object_1.create_report()
        self.report_2 = self.report_object_2.create_report()

    def test_report_object_type_1(self):
        """Test if the report_object is of type Reporter."""
        self.assertIs(type(self.report_object_1), Reporter)

    def test_report_object_type_2(self):
        """Test if the report_object is of type Reporter."""
        self.assertIs(type(self.report_object_2), Reporter)

    def test_report_status_1(self):
        """Test if the report status is SUCCESS."""
        status = self.report_1[1].split(" ")[-1]
        self.assertEqual(status, "SUCCESS")

    def test_report_status_2(self):
        """Test if the report status is SUCCESS."""
        status = self.report_2[1].split(" ")[-1]
        self.assertEqual(status, "SUCCESS")

    def test_report_packages_1(self):
        """Test if the report lists the expected packages."""
        packages = sum([pkg.split(" ", 1)[1:] for pkg in self.report_1[3:7]], [])
        correct_package_list = [
            "dev-libs/openssl 3.0.10:0/3->3.0.11:0/3",
            "net-fs/samba 4.18.4-r1->4.18.8",
            "net-libs/nghttp2 1.51.0:0/1.14->1.57.0:0/1.14",
            "www-client/firefox-bin 118.0.1:rapid->118.0.2:rapid",
        ]
        self.assertEqual(packages, correct_package_list)

    def test_report_packages_2(self):
        """Test if the report lists the expected packages."""
        packages = self.report_2[2:-5]
        correct_package_list = report_2_packages
        self.assertEqual(packages, correct_package_list)

    def test_disk_usage_1(self):
        """Test if the report shows the expected disk usage."""
        disk_usage = self.report_1[-4::]
        correct_disk_usage = [
            "Mount Point /",
            "Free Space 253G => 253G",
            "Used Space 177G => 177G",
            "Used (%) 42% => 42%",
        ]
        self.assertEqual(disk_usage, correct_disk_usage)

    def test_disk_usage_2(self):
        """Test if the report shows the expected disk usage."""
        disk_usage = self.report_2[-4::]
        correct_disk_usage = [
            'Mount Point /',
            'Free Space 260G => 257G',
            'Used Space 170G => 173G',
            'Used (%) 40% => 41%'
        ]
        self.assertEqual(disk_usage, correct_disk_usage)



if __name__ == "__main__":
    unittest.main()
