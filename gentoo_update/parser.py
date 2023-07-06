import re
from typing import Dict, List


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

    def split_log_to_sections(self, log_data: List) -> Dict:
        """
        Splits the log file into sections based on specified markers.

        Returns:
            Dict[str, List[str]]: A dictionary with section names as
                                  keys and content as values.
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
            pretend_status = {"pretend_status": False}
            # function to parse errors during emerge --pretend
            # pretend_details = parse_pretend_details(section_content)
            pretend_details = {"error_type": "", "error_details": ""}
            return {
                "pretend_status": pretend_status,
                "pretend_details": pretend_details,
            }

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
            # function to parse update details
            # update_details = parse_update_details(section_content, type)
            package_list = self.parse_update_details(section_content)
            update_details = {"updated_packages": package_list}
            return {
                "update_status": update_status,
                "update_details": update_details,
            }
        else:
            update_status = False
            # function to parse emerge update errors
            # update_details = parse_update_error_details(section_content, type)
            update_details = {"updated_packages": [], "errors": []}
            return {
                "update_status": update_status,
                "update_details": update_details,
            }

    def parse_update_details(self, section_content: List[str]) -> List[Dict]:
        ebuild_info_pattern = r"\[(.+?)\]"
        package_strings = [
            line
            for line in section_content
            if re.search(ebuild_info_pattern, line)
        ]
        packages = []
        for line in package_strings:
            chunks = line.split()
            ebuild_info = {}
            for chunk in chunks:
                # Match package name and versions
                package_info = re.match(r"^([\w/-]+)-(.*)::gentoo$", chunk)
                if package_info:
                    package_name = package_info.group(1)
                    ebuild_info[package_name] = {}
                    ebuild_info[package_name][
                        "New Version"
                    ] = package_info.group(2)

                # Match update status
                update_status = re.match(r"^(\[ebuild\s+.*\])$", chunk)
                if update_status:
                    ebuild_info[package_name][
                        "Update Status"
                    ] = update_status.group(1)

            old_version = re.search(r'::gentoo\s+\[(.*?)::gentoo\]', line)
            print(old_version)
            if old_version:
                ebuild_info[package_name]["Old Version"] = old_version.group(1)

            # Match USE flags
            use_flags = re.search(r'USE="(.*?)"', line)
            if use_flags:
                ebuild_info[package_name]["USE Flags"] = use_flags.group(1)

            # Match multilibs
            multilibs = re.search(r'(ABI_X86=".*?")', line)
            if multilibs:
                ebuild_info[package_name]["Multilibs"] = multilibs.group(1)

            # Match size
            size = re.search(r"(\d+\s+KiB)", line)
            if size:
                ebuild_info[package_name]["Size"] = size.group(1)

            packages.append(ebuild_info)
        return packages

    def extract_info_for_report(self) -> Dict:
        """
        Extract information about the update from the log file.

        Returns:
            Dict: A dictionary that contains the
                  parsed data from all sections.
        """
        info = {}
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

        return info

    def create_failed_report(self, update_info) -> List:
        """
        Create a report when update failes.
        """
        # do failed report processing
        return []

    def create_successful_report(self, update_info) -> List:
        """
        Create a report when update is successful.
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
                report.append(f"--- {package_name}")

        return report

    def create_report(self) -> List:
        """
        Create a report.
        """
        info = self.extract_info_for_report()
        print(info)
        update_info = info["update_system"]
        update_success = update_info["update_status"]
        if update_success:
            report = self.create_successful_report(update_info)
            return report
        else:
            report = self.create_failed_report(update_info)
            return report


if __name__ == "__main__":
    report = Parser("./log_for_tests").create_report()
    # for line in report:
    #    print(line)
