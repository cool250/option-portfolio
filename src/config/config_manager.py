import logging
import os

from dotenv import load_dotenv

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

"""


class ConfigManager:
    _instance = None

    @staticmethod
    def getInstance():
        if ConfigManager._instance is None:
            ConfigManager._instance = ConfigManager()
        return ConfigManager._instance

    def __init__(self):
        dotenv_path = os.getenv("ENVIRONMENT_FILE")
        logging.info(f"dotenv_path : {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path, override=True)

    def getConfig(self, key):
        return os.environ.get(key)
