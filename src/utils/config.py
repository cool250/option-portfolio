import configparser

"""
ConfigManager Class
-------------------

A class to manage configurations using the configparser module.

Attributes:
---------

* _instance : A static variable to hold the single instance of the class.
* config : An instance of the configparser.ConfigParser class.
* file_path : The path to the configuration file.

Methods:
-------

* getInstance() : Returns the single instance of the class.
* __init__() : Initializes the object with the configuration file path.
* setConfig() : Sets the configuration object.
* getConfig() : Gets the configuration object.

Raises:
------

* ValueError : If the configuration file cannot be read.

Examples:
--------

>>> config_manager = ConfigManager('config.ini')
>>> config_manager.setConfig({'section': {'option': 'value'}})
>>> config_manager.getConfig('section', 'option')
'value'
"""


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

    def setConfig(self, config):
        self.config = config

    def getConfig(self, *args):
        return self.config.get(*args)
