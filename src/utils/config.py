import configparser


class Config(object):
    CONFIGURATION = None

    def __init__(self):
        if Config.CONFIGURATION is None:
            config = configparser.ConfigParser()
            file_path = "config.ini"
            config.read(file_path)
            Config.CONFIGURATION = config

    def get(self, *args):
        response = self.CONFIGURATION.get(*args)
        return response
