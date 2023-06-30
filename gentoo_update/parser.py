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

    def split_log_to_sections(self, log_data: List) -> Dict[str, List[str]]:
        """
        Splits the log file into sections based on specified markers.

        Returns:
            Dict[str, List[str]]: A dictionary with section names as keys and content as values.
        """
        section_pattern = r"\{\{(.+?)\}\}"

        section_name = "beginning"
        log_by_sections: Dict[str, List[str]] = {}
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


if __name__ == "__main__":
    parser = Parser("./log_for_tests")
    pprint.pprint(parser.log_data["{{ UPDATE SYSTEM }}"])
