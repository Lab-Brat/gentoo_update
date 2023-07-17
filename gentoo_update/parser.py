import re
from typing import Dict, List, Tuple


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

    def parse_emerge_pretend_section(self, section_content: List[str]) -> Dict:
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
            return {
                "pretend_status": pretend_status,
                "pretend_details": pretend_details,
            }
        else:
            pretend_status = False
            # function to parse errors during emerge --pretend
            pretend_details = self.parse_pretend_details(section_content)
            return {
                "pretend_status": pretend_status,
                "pretend_details": pretend_details,
            }

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

    def parse_pretend_details(self, section_content: List[str]) -> Dict:
        """
        Parse information about the emerge pretend from logs.

        Parameters:
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
            List[Dict]: A list of dictionaries where each item is
                a named dictionary containing useful information for the report.
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
        pretend_details = {
            "error_type": error_type,
            "error_details": error_details,
        }
        return pretend_details

    def parse_update_system_section(self, section_content: List[str]) -> Dict:
        """
        Function to parse the "update system" section of the log data.

        Parameters:
            section_content (List[str]): A list of strings that contains
                    the content of the "update system" section.

        Returns:
            Dict: A dictionary that contains the status
                  of the system update and the details.
        """
        update_type = section_content[1].split()[1]
        if "update was successful" in section_content:
            update_status = True
            package_list = self.parse_update_details(section_content)
            update_details = {"updated_packages": package_list}
            return {
                "update_type": update_type,
                "update_status": update_status,
                "update_details": update_details,
            }
        else:
            update_status = False
            # function to parse emerge update errors
            # update_details = parse_update_error_details(section_content, type)
            update_details = {"updated_packages": [], "errors": []}
            return {
                "update_type": update_type,
                "update_status": update_status,
                "update_details": update_details,
            }

    def _parse_update_get_packages_names(
        self, name_and_version: str
    ) -> Tuple[str, str]:
        """
        Parse package name and new version.

        Parameters:
            name_and_version (str): String containing package information.
            example:
                sys-process/procps-3.3.17-r2:0/8::gentoo

        Returns:
            Tuple: tuple containing package name and it's new version
            example:
                (sys-process/procps, 3.3.17-r2:0/8)
        """
        regex_package_info = (
            r"^(.+?)-"  # regex_package_name
            r"("
            r"(?:(?<=-)[a-z]{2,}|[0-9]+(?:\.[0-9]+)*)"  # regex_version_number
            r"(?:_p[0-9]+)?"  # regex_optional_patch
            r"(?:-r[0-9]+)?"  # regex_optional_revision
            r"(?::[0-9]+(?:/[0-9]+(\.[0-9]+)?)?)?"  # regex_optional_sub_version
            r")"
            r"(?::|$)"  # regex end
        )
        package_regex = re.compile(regex_package_info)
        match = package_regex.search(name_and_version)
        if match:
            package_name, new_version, _ = match.groups()
            return package_name, new_version
        else:
            return ("undefined", "undefined")

    def parse_update_details(self, section_content: List[str]) -> List[Dict]:
        """
        Parse information about the update from logs.

        Parameters:
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
            List[Dict]: A list of dictionaries where each item is
                a named dictionary containing useful information for the report.
        """
        ebuild_info_pattern = r"\[(.+?)\]"
        package_strings = [
            line
            for line in section_content
            if re.search(ebuild_info_pattern, line) and line != "[ ok ]"
        ]
        packages = []
        for line in package_strings:
            chunks = re.findall(r'\S+=".*?"|\[.*?\]|\S+', line)
            package_name, new_version = self._parse_update_get_packages_names(
                chunks[1]
            )
            ebuild_info = {
                package_name: {
                    "New Version": new_version,
                    "Old Version": "undefined",
                    "Update Status": "undefined",
                    "USE Flags": "undefined",
                    "Multilibs": "undefined",
                }
            }

            for chunk in chunks:
                # Match update status
                update_status = re.match(r"^(\[ebuild\s+.*\])$", chunk)
                if update_status:
                    ebuild_info[package_name][
                        "Update Status"
                    ] = update_status.group(1)

                old_version = re.search(r"\[(.*)(::gentoo)\]", chunk)
                if old_version:
                    ebuild_info[package_name][
                        "Old Version"
                    ] = old_version.group(1)

                # Match USE flags
                use_flags = re.search(r'USE="(.*?)"', chunk)
                if use_flags:
                    ebuild_info[package_name]["USE Flags"] = use_flags.group(1)

                # Match multilibs
                multilibs = re.search(r'(ABI_X86=".*?")', chunk)
                if multilibs:
                    ebuild_info[package_name]["Multilibs"] = multilibs.group(1)

            packages.append(ebuild_info)
        return packages

    def parse_disk_usage_info(self, section_content: List[str]) -> Dict:
        """
        Get disk usage information.

        Parameters:
            section_content (List[str]): A list where each item is
                one line of logs from a section.

        Returns:
            Dict: A dictionary containing statistics of disk usage.
        """
        disk_usage = {}
        split_content = section_content[1].split(" ===> ")
        split_content = split_content[1].split(", ")
        for stat in split_content:
            stat = stat.split("=")
            disk_usage[stat[0]] = stat[1]

        return disk_usage

    def extract_info_for_report(self) -> Dict:
        """
        Extract information about the update from the log file.

        Returns:
            Dict: A dictionary that contains the
                  parsed data from all sections.
        """
        info = {"disk_usage": {}}
        for section in self.log_data.keys():
            section_content = self.log_data[section]
            if section == "pretend_emerge":
                info[section] = self.parse_emerge_pretend_section(
                    section_content
                )
            elif section == "update_system":
                info[section] = self.parse_update_system_section(
                    section_content
                )
            elif "calculate_disk_usage" in section:
                info["disk_usage"][section] = self.parse_disk_usage_info(
                    section_content
                )

        return info
