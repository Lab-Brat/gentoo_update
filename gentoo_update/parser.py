import pprint

class Parser:
    def __init__(self, log_file):
        self.log_file = log_file
        self.log_data = self.read_log()

    def read_log(self):
        with open(self.log_file, 'r') as f:
            log_data = f.readlines()
        return log_data

    def split_log_to_sections(self):
        section_name = 'beginning'
        log_by_sections = {}
        for line in self.log_data:
            if ' ::: ' in line:
                line = line.split(' ::: ')[1]
                if line.startswith('{{'):
                    section_name = line
                    log_by_sections[section_name] = []
                else:
                    log_by_sections[section_name].append(line)
            else:
                log_by_sections['final'] = line
        
        return log_by_sections


if __name__ == '__main__':
    parser = Parser('./log_for_tests')
    sections = parser.split_log_to_sections()
    pprint.pprint(sections)
