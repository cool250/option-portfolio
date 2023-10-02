import json
import logging


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class JSONReader(metaclass=SingletonMeta):
    """
    This class implements the Singleton design pattern to ensure only one
    instance is created. It loads JSON data from a file path provided.

    Parameters:
        json_file_path (str): The path to the JSON file to load.

    Attributes:
        json_file_path (str): The path to the JSON file.
        data (dict): The loaded JSON data.

    Methods:
        load_data(): Loads the JSON data from the file path and returns it.
    """

    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = self.load_data()

    def load_data(self):
        logging.info("Loading Account Data")
        try:
            with open(self.json_file_path, "r") as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError:
            print(f"File not found: {self.json_file_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
