import sys
from typing import List
from .parser import (
    UpdateSection,
    PretendError,
    PretendSection,
    DiskUsage,
    LogInfo,
)


class Reporter:
    def __init__(self, update_info: LogInfo) -> None:
        self.info = update_info

    def _create_failed_pretend_report(
        self, pretend_info: PretendSection
    ) -> List[str]:
        """
        Create a report when emerge pretend fails.

        Parameters:
            pretend_info (PretendSection): emerge pretend information.

        Returns:
            List: A list of strings that comprise the failed pretend report.
        """
        report = [
            "==========> Gentoo Update Report <==========",
            "emerge pretend status: FAIL",
        ]
        pretend_details = pretend_info.pretend_details
        if pretend_details.error_type == "undefined":
            report.append("Could not identify error, please check the logs")
        elif pretend_details.error_type == "Blocked Packages":
            report.append(f"\nError Type: {pretend_details.error_type}")
            report.extend(self._report_blocked_packages(pretend_details))
        report.append("")
        return report

    def _report_blocked_packages(
        self, pretend_details: PretendError
    ) -> List[str]:
        """
        Report on Blocked Packages error during emerge pretend.

        Parameters:
            pretend_details (PretendError): In this case it's blocked packages.

        Returns:
            List[str]: Section of the report about blocked packages.
        """
        blocked_packages_report = ["List of Blocked Packages:"]
        for package in pretend_details.error_details:
            blocked_packages_report.append(f"-----> {package}")

        return blocked_packages_report

    def _create_failed_report(
        self, update_info: UpdateSection, disk_usage_info: DiskUsage
    ) -> List[str]:
        """
        Create a report when update fails.

        Parameters:
            update_info (LogInfo.UpdateSection): Update information.
            disk_usage_inf (LogInfo.DiskUsage): Disk usage information.

        Returns:
            List: A list of strings that comprise the failed update report.
        """
        # do failed report processing
        return ["Your update is a failure"]

    def _create_successful_report(
        self, update_info: UpdateSection, disk_usage_info: DiskUsage
    ) -> List[str]:
        """
        Create a report when update succeeds.

        Parameters:
            update_info (LogInfo.UpdateSection): Update information.
            disk_usage_inf (LogInfo.DiskUsage): Disk usage information.

        Returns:
            List: A list of strings that comprise the successful update report.
        """
        report = [
            "==========> Gentoo Update Report <==========",
            "update status: SUCCESS",
        ]
        updated_packages = update_info.update_details["updated_packages"]
        other_package_types = False
        if updated_packages:
            report.append(r"processed packages:")
            for package in updated_packages:
                if package.package_type == "ebuild":
                    package_name = package.package_name
                    new_version = package.new_version
                    old_version = package.old_version
                    report.append(
                        f"--- {package_name} {old_version}->{new_version}"
                    )
                else:
                    other_package_types = True

            if other_package_types:
                report.append("")
                report.append("Non-ebuild packages")
                for package in updated_packages:
                    if package.package_type == "blocks":
                        package_name = package.package_name
                        blocked_package = package.blocked_package
                        report.append(
                            f"--- {package_name} blocked {blocked_package}"
                        )
                    elif package.package_type == "uninstall":
                        package_name = package.package_name
                        uninstalled_package = package.uninstalled_package
                        report.append(f"--- {package_name} was uninstalled")
            report.append("")
            report.append("Disk Usage Stats:")

            for before, after in zip(
                disk_usage_info.before_update, disk_usage_info.after_update
            ):
                disk_usage_stats = (
                    f"Mount Point {before.mount_point}\n"
                    f"Free Space {before.free} => {after.free}\n"
                    f"Used Space {before.used} => {after.used}\n"
                    f"Used pc(%) {before.percent_used} => {after.percent_used}\n"
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
        try:
            disk_usage_info = info.disk_usage
            pretend_success = info.pretend_emerge.pretend_status

            if pretend_success:
                update_info = info.update_system
                update_success = info.update_system.update_status
            else:
                pretend_info = info.pretend_emerge
                update_success = False

            if update_success:
                report = self._create_successful_report(
                    update_info, disk_usage_info
                )
            elif pretend_success and not update_success:
                report = self._create_failed_report(
                    update_info, disk_usage_info
                )
            else:
                report = self._create_failed_pretend_report(pretend_info)
            return report
        except AttributeError:
            print("[Error] Could not create the report, incomplete log file")
            sys.exit(1)

    def print_report(self) -> None:
        """
        Print the report line by line to console.
        """
        report = self.create_report()
        for line in report:
            print(line)
