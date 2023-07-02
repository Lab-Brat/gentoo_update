import re
import pprint
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
            update_details = {"updated_packages": []}
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


if __name__ == "__main__":
    report = Parser("./log_for_tests").extract_info_for_report()
    pprint.pprint(report)
