"""Classes and methods for parsing log files.

Specifically logfiles generated by Gentoo Linux's emerge package manager.
"""

import re
from typing import Dict, List, Tuple

from .parser_package import PackageParser
from .report_objects import (
    DiskUsage,
    DiskUsageStats,
    LogInfo,
    PretendError,
    PretendSection,
    UpdateSection,
)


class Parser:
    """A class that provides methods to parse log files.

    Attributes
    ----------
    log_file (str): The name of the log file.
    log_data (List[str]): The content of the log file as a list of strings.
    """

    def __init__(self, log_file: str) -> None:
        """Initialize the Parser with a log file.

        Args:
        ----
            log_file: The name of the log file.
        """
        self.log_file = log_file
        self.log_data = self.read_log()

    def read_log(self) -> Dict:
        """Read the log file and returns its content.

        Returns
        -------
            Dict: A dictionary with section names as keys
                and content as values.
        """
        with open(self.log_file, encoding="utf-8") as log_file:
            log_data = log_file.readlines()
        return self.split_log_to_sections(log_data)

    def split_log_to_sections(self, log_data: List[str]) -> Dict:
        """Split the log file into sections based on {{ ... }} marker.

        Args:
        ----
            log_data (List[str]): Log content read with read_log method.

        Returns:
        -------
            Dict: A dictionary with section names as keys
                and content as values.
        """
        section_pattern = r"\{\{(.+?)\}\}"
        section_name = "beginning"
        log_by_sections: Dict[str, List[str]] = {section_name: []}

        for log_line in log_data:
            if " ::: " in log_line:
                line = log_line.split(" ::: ")[1].strip()
                match_section_pattern = re.search(section_pattern, line)
                if match_section_pattern:
                    section_name = "_".join(line.split()[1:-1]).lower()
                    log_by_sections[section_name] = []
                else:
                    log_by_sections[section_name].append(line)
            else:
                if log_by_sections.get("final") is None:
                    log_by_sections["final"] = []
                else:
                    log_by_sections["final"].append(log_line)

        return log_by_sections

    def parse_emerge_pretend_section(
        self, section_content: List[str]
    ) -> PretendSection:
        """Parse the "emerge pretend" section of the log data.

        Args:
        ----
            section_content (List[str]): A list of strings that contains
                        the content of the "emerge pretend" section.

        Returns:
        -------
            PrentedSection: object that contains the status of
                  the "emerge pretend" operation and the details.
        """
        if (
            "emerge pretend was successful, updating..."
            or "There are no packages to update, skipping..." in section_content
        ):
            pretend_status = True
            pretend_details = None
        else:
            pretend_status = False
            pretend_details = self.parse_pretend_details(section_content)
        return PretendSection(pretend_status, pretend_details)

    def _parse_pretend_get_blocked_details(self, error_content: List[str]) -> List[str]:
        """Parse details of blocked package error.

        Args:
        ----
            error_content (List[str]): Lines from log marked ERROR by logger.

        Returns:
        -------
            List[str]: Parsed packages tht cause the error.
        """
        blocked_packages = []
        for line in error_content:
            match_package_pattern = re.search(r"^\((.+?)\)", line)
            if match_package_pattern:
                blocked_packages.append(match_package_pattern.group(1))

        return blocked_packages

    def _parse_pretend_get_error_type(
        self, error_content
    ) -> Tuple[str, str, List[str]]:
        """Parse error type and error details.

        Args:
        ----
            error_content (List[str]): Lines from log marked ERROR by logger.

        Returns:
        -------
            Tuple[str, str, List[str]]: Return error type, error definition as
              strings and error details as a list of strings.
        """
        error_type = "undefined"
        error_definition = "undefined"
        error_details = "undefined"

        for line in error_content:
            if "Blocked Packages" in line:
                error_type = "Blocked Packages"
                error_details = self._parse_pretend_get_blocked_details(error_content)

        for line in error_content:
            if line[0] == "*":
                error_definition += f"{line[2:]} "

        return (error_type, error_definition, error_details)

    def parse_pretend_details(self, section_content: List[str]) -> PretendError:
        """Parse information about the emerge pretend from logs.

        Args:
        ----
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
        -------
            PretendError: Dataclass that contains details about failed pretend,
                for example a list of blocked packages.
        """
        error_index = section_content.index("emerge pretend has failed, exiting")
        error_content = [line for line in section_content[error_index + 1 :] if line]

        error_type, _, error_details = self._parse_pretend_get_error_type(error_content)

        return PretendError(error_type, error_details)

    def parse_update_system_section(self, section_content: List[str]) -> UpdateSection:
        """Parse the "update system" section of the log data.

        Args:
        ----
            section_content (List[str]): A list of strings that contains
                    the content of the "update system" section.

        Returns:
        -------
            UpdateSection: A dataclass that contains the status
                  of the system update and package details.
        """
        try:
            update_type = (
                "@world" if section_content[2].split()[1] == "@world" else "security"
            )
        except IndexError:
            update_type = "Undefined"

        if "update was successful" in section_content:
            update_status = True
            if "Nothing to merge; quitting" in section_content:
                update_details = {"updated_packages": [], "errors": []}
            else:
                package_list = PackageParser().parse_update_details(section_content)
                update_details = {"updated_packages": package_list}
        elif "There are no packages to update, skipping..." in section_content:
            update_status = True
            update_type = "security"
            update_details = {"updated_packages": [], "errors": []}
        else:
            update_status = False
            update_details = {"updated_packages": [], "errors": []}
        return UpdateSection(update_type, update_status, update_details)

    def parse_disk_usage_info(self, section_content: List[str]) -> List[DiskUsageStats]:
        """Get disk usage information.

        Args:
        ----
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
        -------
            List[DiskUsageStats]: A list of DiskUsageStats objects
                for each mount point containing statistics of disk usage.
        """
        mount_point_lines = [
            line for line in section_content if line[0:14] == "Disk usage for"
        ]
        mount_points = []

        for line in mount_point_lines:
            split_content = line.split(" ===> ")
            stats = split_content[1].split(", ")

            mount_point = split_content[0].replace("Disk usage for ", "")
            total = stats[0].split("=")[1]
            used = stats[1].split("=")[1]
            free = stats[2].split("=")[1]
            percent_used = stats[3].split("=")[1]

            disk_usage_stats = DiskUsageStats(
                mount_point, total, used, free, percent_used
            )
            mount_points.append(disk_usage_stats)

        return mount_points

    def extract_info_for_report(self) -> LogInfo:
        """Extract information about the update from the log file.

        Returns
        -------
            LogInfo: Dataclass containing parsed data from all sections.
        """
        log_info = LogInfo
        disk_usage = DiskUsage
        for section, section_content in self.log_data.items():
            if section == "pretend_emerge":
                log_info.pretend_emerge = self.parse_emerge_pretend_section(
                    section_content
                )
            elif section == "update_system":
                log_info.update_system = self.parse_update_system_section(
                    section_content
                )
            elif section == "calculate_disk_usage_1":
                disk_usage.before_update = self.parse_disk_usage_info(section_content)
            elif section == "calculate_disk_usage_2":
                disk_usage.after_update = self.parse_disk_usage_info(section_content)
        log_info.disk_usage = disk_usage

        return log_info
