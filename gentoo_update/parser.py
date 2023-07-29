import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PackageInfo:
    package_name: str
    new_version: str
    old_version: str
    update_status: str
    repo: str

    def add_attributes(self, attrs):
        for attr_name, attr_value in attrs.items():
            setattr(self, attr_name, attr_value)


@dataclass
class UpdateSection:
    update_type: str
    update_status: bool
    update_details: Dict[str, PackageInfo]


@dataclass
class PretendError:
    error_type: str
    error_details: List[str]


@dataclass
class PretendSection:
    pretend_status: bool
    pretend_details: PretendError


@dataclass
class DiskUsageStats:
    mount_point: str
    total: str
    used: str
    free: str
    percent_used: str


@dataclass
class DiskUsage:
    before_update: List[DiskUsageStats]
    after_update: List[DiskUsageStats]


@dataclass
class LogInfo:
    pretend_emerge: Optional[PretendSection]
    update_system: Optional[UpdateSection]
    disk_usage: Optional[DiskUsage]


class Parser:
    def __init__(self, log_file: str) -> None:
        """
        Initialize the Parser with a log file.

        Parameters:
            log_file: The name of the log file.
        """
        self.log_file = log_file
        self.log_data = self.read_log()

    def read_log(self) -> List[str]:
        """
        Reads the log file and returns its content.

        Returns:
            List[str]: The content of the log file as a list of strings.
        """
        with open(self.log_file, "r") as log_file:
            log_data = log_file.readlines()
        return self.split_log_to_sections(log_data)

    def split_log_to_sections(self, log_data: List[str]) -> Dict:
        """
        Splits the log file into sections based on specified markers.

        Parameters:
            log_data (List[str]): Log content read with read_log method.

        Returns:
            Dict: A dictionary with section names as keys
                and content as values.
        """
        section_pattern = r"\{\{(.+?)\}\}"
        section_name = "beginning"
        log_by_sections: Dict[str, List[str]] = {section_name: []}

        for line in log_data:
            if " ::: " in line:
                line = line.split(" ::: ")[1].strip()
                match_section_pattern = re.search(section_pattern, line)
                if match_section_pattern:
                    section_name = "_".join(line.split()[1:-1]).lower()
                    log_by_sections[section_name] = []
                else:
                    log_by_sections[section_name].append(line)
            else:
                log_by_sections["final"] = line

        return log_by_sections

    def parse_emerge_pretend_section(
        self, section_content: List[str]
    ) -> PretendSection:
        """
        Function to parse the "emerge pretend" section of the log data.

        Parameters:
            section_content (List[str]): A list of strings that contains
                        the content of the "emerge pretend" section.

        Returns:
            Dict: A dictionary that contains the status of
                  the "emerge pretend" operation and the details.
        """
        if "emerge pretend was successful, updating..." in section_content:
            pretend_status = True
            pretend_details = None
        else:
            pretend_status = False
            pretend_details = self.parse_pretend_details(section_content)
        return PretendSection(pretend_status, pretend_details)

    def _parse_pretend_get_blocked_details(
        self, error_content: List[str]
    ) -> List[str]:
        """
        Parse details of blocked package error.

        Parameters:
            error_content (List[str]): Lines from log marked as ERROR by logger.

        Returns:
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
        """
        Parse error type and error details.

        Parameters:
            error_content (List[str]): Lines from log marked as ERROR by logger.

        Returns:
            Tuple[str, str, List[str]]: Return error type, error definition as strings
                and error details as a list of strings.
        """
        error_type = "undefined"
        error_definition = "undefined"
        error_details = "undefined"

        for line in error_content:
            if "Blocked Packages" in line:
                error_type = "Blocked Packages"
                error_details = self._parse_pretend_get_blocked_details(
                    error_content
                )

        for line in error_content:
            if line[0] == "*":
                error_definition += f"{line[2:]} "

        return (error_type, error_definition, error_details)

    def parse_pretend_details(self, section_content: List[str]) -> PretendError:
        """
        Parse information about the emerge pretend from logs.

        Parameters:
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
            PretendError: A datalass that contains details about failed pretend,
                for example a list of blocked packages.
        """
        error_index = section_content.index(
            "emerge pretend has failed, exiting"
        )
        error_content = [
            line for line in section_content[error_index + 1 :] if line
        ]

        error_type, _, error_details = self._parse_pretend_get_error_type(
            error_content
        )

        return PretendError(error_type, error_details)

    def parse_update_system_section(
        self, section_content: List[str]
    ) -> UpdateSection:
        """
        Function to parse the "update system" section of the log data.

        Parameters:
            section_content (List[str]): A list of strings that contains
                    the content of the "update system" section.

        Returns:
            UpdateSection: A dataclass that contains the status
                  of the system update and package details.
        """
        update_type = section_content[1].split()[1]
        if "update was successful" in section_content:
            update_status = True
            package_list = self.parse_update_details(section_content)
            update_details = {"updated_packages": package_list}
        else:
            update_status = False
            update_details = {"updated_packages": [], "errors": []}
        return UpdateSection(update_type, update_status, update_details)

    def parse_package_string(self, package_string: str) -> List[str]:
        """
        Parse package string into multiple parts.

        Parameters:
            package_string (str): String containing package information.

        Returns:
            List: List containing package information parts.
        """
        split_package_string = []
        temp = ""
        quotes_count = 0
        brackets_count = 0

        for char in package_string:
            temp += char
            if char == '"':
                quotes_count += 1
            elif char == "[":
                brackets_count += 1
            elif char == "]":
                brackets_count -= 1

            if char == " " and quotes_count % 2 == 0 and brackets_count == 0:
                split_package_string.append(temp.strip())
                temp = ""

        if temp:
            split_package_string.append(temp.strip())

        return split_package_string

    def parse_update_details(
        self, section_content: List[str]
    ) -> List[PackageInfo]:
        """
        Parse information about update from log file.

        Parameters:
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
            List[PackageInf]o: List of PackageInfo objects where each object
                contains useful information for the report.
        """
        ebuild_info_pattern = r"\[(.+?)\]"
        package_strings = [
            line
            for line in section_content
            if re.search(ebuild_info_pattern, line) and line != "[ ok ]"
        ]
        packages = []
        for package_string in package_strings:
            split_package_string = self.parse_package_string(package_string)
            update_status = split_package_string[0]

            package_base_info = split_package_string[1]
            repo = package_base_info.split("::")[1]
            name_newversion = package_base_info.split("::")[0]

            package_name = ""
            for part in name_newversion.split("-"):
                if part.isnumeric() == True:
                    pass
                elif "." in part:
                    pass
                elif len(part) == 2 and part[0] == "r" and part[1].isnumeric():
                    pass
                else:
                    package_name += f"{part}-"

            new_version = name_newversion.replace(package_name, "")
            old_version = split_package_string[2].split("::")[0][1:]
            package_name = package_name[:-1]

            ebuild_info = PackageInfo(
                package_name, new_version, old_version, update_status, repo
            )

            for var in split_package_string:
                if '="' in var:
                    var = var.split("=")
                    ebuild_info.add_attributes(
                        {var[0]: var[1][1:-1].split(" ")}
                    )

            packages.append(ebuild_info)
        return packages

    def parse_disk_usage_info(
        self, section_content: List[str]
    ) -> List[DiskUsageStats]:
        """
        Get disk usage information.

        Parameters:
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
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
        """
        Extract information about the update from the log file.

        Returns:
            LogInfo: Dataclass containing parsed data from all sections.
        """
        log_info = LogInfo
        disk_usage = DiskUsage
        for section in self.log_data.keys():
            section_content = self.log_data[section]
            if section == "pretend_emerge":
                log_info.pretend_emerge = self.parse_emerge_pretend_section(
                    section_content
                )
            elif section == "update_system":
                log_info.update_system = self.parse_update_system_section(
                    section_content
                )
            elif section == "calculate_disk_usage_1":
                disk_usage.before_update = self.parse_disk_usage_info(
                    section_content
                )
            elif section == "calculate_disk_usage_2":
                disk_usage.after_update = self.parse_disk_usage_info(
                    section_content
                )
        log_info.disk_usage = disk_usage
        return log_info


if __name__ == "__main__":
    report = Parser("./log_blocks").extract_info_for_report()
    print(report.pretend_emerge)
