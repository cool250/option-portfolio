import configparser


class ConfigManager:
    _instance = None

    @staticmethod
    def getInstance():
        if ConfigManager._instance is None:
            ConfigManager._instance = ConfigManager()
        return ConfigManager._instance

    def __init__(self):
        self.config = configparser.ConfigParser()
        file_path = "config.ini"
        self.config.read(file_path)

    def getConfig(self, *args):
        return self.config.get(*args)
