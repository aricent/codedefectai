from configparser import ConfigParser


class CDPParser:
    def __init__(self, config_file):
        self.parser = ConfigParser()
        self.parser.read(config_file)

    def get_config(self, section, key):
        return self.parser.get(section, key)

    def get_section_items(self, section):
        dictionary = {}
        for name, value in self.parser.items(section):
            dictionary[name] = value

        return dictionary


class ConfigFetcher:
    def __init__(self, config_file):
        self.configFetcher = CDPParser(config_file)

    def get(self, key, section="default"):
        return self.configFetcher.get_config(section, key)

    def get_projects(self, section):
        return self.configFetcher.get_section_items(section)
