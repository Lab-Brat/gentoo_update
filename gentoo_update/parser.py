import re
import sys
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
        self.split_sections()

    def read_log(self) -> List[str]:
        """
        Reads the log file and returns its content.

        Returns:
            List[str]: The content of the log file as a list of strings.
        """
        with open(self.log_file, "r") as log_file:
            log_data = log_file.readlines()
        return self.split_log_to_sections(log_data)

    def split_log_to_sections(self, log_data: List) -> Dict[str, List[str]]:
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
                    section_name = line
                    log_by_sections[section_name] = []
                else:
                    log_by_sections[section_name].append(line)
            else:
                log_by_sections["final"] = line

        return log_by_sections

    def split_sections(self):
        for section in self.log_data.keys():
            section_content = self.log_data[section]
            if section == "{{ PRETEND EMERGE }}":
                self.split_emerge_pretend_section(section_content)
            elif section == "{{ UPDATE SYSTEM }}":
                self.split_update_system_section(section_content)
        print("Section parsing finished!")

    def split_emerge_pretend_section(self, section_content: List[str]):
        pretend_successful = (
            "emerge pretend was successful, updating..." in section_content
        )
        if pretend_successful:
            print("Pretend completed without errors")
        else:
            print("Pretend exited with errors: ")
            print("Error 1: ....")
            print("Error 2: ....")

    def split_update_system_section(self, section_content: List[str]):
        update_type = section_content[1].split()[1]
        if update_type == "@world":
            pass
        elif update_type == "GLSA":
            pass
        else:
            print(f"{update_type} is a wrong update type")
            print("Correct types: @world and GLSA")
            sys.exit(0)


if __name__ == "__main__":
    parser = Parser("./log_for_tests")
