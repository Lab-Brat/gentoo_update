from typing import Dict, List


class Reporter:
    def __init__(self, update_info) -> None:
        self.info = update_info
        self.report = self.create_report()

    def create_failed_pretend_report(self, pretend_info: Dict) -> List[str]:
        """
        Create a report when emerge pretend fails.

        Parameters:
            pretend_info (Dict): emerge pretend information parsed by
                parse_emerge_pretend_section.

        Returns:
            List: A list of strings that comprise the failed pretend report.
        """
        report = [
            "==========> Gentoo Update Report <==========",
            "emerge pretend status: FAIL",
        ]
        pretend_details = pretend_info["pretend_details"]
        if pretend_details["error_type"] == "undefined":
            report.append("Could not identify error, please check the logs")
        else:
            report.append(f"\nError Type: {pretend_details['error_type']}")
            report.extend(self._report_blocked_packages(pretend_details))
        report.append("")
        return report

    def _report_blocked_packages(self, pretend_details: List[str]) -> List[str]:
        """
        Report on Blocked Packages error during emerge pretend.

        Parameters:
            pretend_details (List[str]): In this case it's blocked packages.

        Returns:
            List[str]: Section of the report about blocked packages.
        """
        blocked_packages_report = ["List of Blocked Packages:"]
        for package in pretend_details["error_details"]:
            blocked_packages_report.append(f"-----> {package}")

        return blocked_packages_report

    def create_failed_report(
        self, update_info: List[Dict], disk_usage_info: Dict
    ) -> List[str]:
        """
        Create a report when update failes.

        Parameters:
            update_info (List[Dict]): Update information parsed by
                self.parse_update_details.
            disk_usage_inf (Dict): Disk usage information parsed by
                self.parse_disk_usage_info.

        Returns:
            List: A list of strings that comprise the failed update report.
        """
        # do failed report processing
        return ["Your update is a failure"]

    def create_successful_report(
        self, update_info: List[Dict], disk_usage_info: Dict
    ) -> List[str]:
        """
        Create a report when update succeeds.

        Parameters:
            update_info (List[Dict]): Update information parsed by
                self.parse_update_details.
            disk_usage_inf (Dict): Disk usage information parsed by
                self.parse_disk_usage_info.

        Returns:
            List: A list of strings that comprise the successful update report.
        """
        report = [
            "==========> Gentoo Update Report <==========",
            "update status: SUCCESS",
        ]
        updated_packages = update_info["update_details"]["updated_packages"]
        if updated_packages:
            report.append(r"processed packages:")
            for package in updated_packages:
                package_name = list(package.keys())[0]
                new_version = package[package_name]["New Version"]
                old_version = package[package_name]["Old Version"]
                report.append(
                    f"--- {package_name} {old_version}->{new_version}"
                )
            report.append("")

            disk_usage_before = disk_usage_info["calculate_disk_usage_1"]
            disk_usage_after = disk_usage_info["calculate_disk_usage_2"]
            disk_usage_stats = (
                "Disk Usage Stats:\n"
                f"Free Space {disk_usage_before['Free']} => {disk_usage_after['Free']}\n"
                f"Used Space {disk_usage_before['Used']} => {disk_usage_after['Used']}\n"
                f"Used pc(%) {disk_usage_before['Percent used']} => {disk_usage_after['Percent used']}\n"
            )
            report.append(disk_usage_stats)

        return report

    def create_report(self) -> List[str]:
        """
        Create a report.

        Returns:
            List: A list of strings that comprise the update report.
        """
        info = self.info
        disk_usage_info = info["disk_usage"]
        pretend_success = info["pretend_emerge"]["pretend_status"]

        if pretend_success:
            update_info = info["update_system"]
            update_success = info["update_system"]["update_status"]
        else:
            pretend_info = info["pretend_emerge"]
            update_success = False

        if update_success:
            report = self.create_successful_report(update_info, disk_usage_info)
            return report
        elif pretend_success and not update_success:
            report = self.create_failed_report(update_info, disk_usage_info)
        else:
            report = self.create_failed_pretend_report(pretend_info)
            return report
