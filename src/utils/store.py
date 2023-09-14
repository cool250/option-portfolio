import dbm
import json
import logging
from abc import ABC, abstractmethod

import redis

from utils.config import ConfigManager
from utils.exceptions import HaltCallbackException


class Store_Factory:
    def get_store():
        cache_type = ConfigManager.getInstance().getConfig("CACHE", "CACHE_TYPE")
        if cache_type == "local":
            return LocalStore()
        else:
            return RedisStore()


class Store(ABC):
    @abstractmethod
    def set_dict(self, key, val):
        pass

    def get_dict(self, key):
        pass


class RedisStore(Store):
    def __init__(self):
        config = Config()
        host = ConfigManager.getInstance().getConfig("REDIS", "HOST")
        port = ConfigManager.getInstance().getConfig("REDIS", "PORT")
        password = ConfigManager.getInstance().getConfig("REDIS", "PWD")
        self.client = redis.StrictRedis(
            host,
            port,
            password,
            decode_responses=True,
        )

    def set_dict(self, key, val):
        # Convert Dict to JSON string
        json_val = json.dumps(val)
        try:
            self.client.set(key, json_val)
        except redis.exceptions.ConnectionError as err:
            raise HaltCallbackException("Unable to connect", err)

    def get_dict(self, key):
        try:
            json_string = self.client.get(key)
        except redis.exceptions.ConnectionError as err:
            raise HaltCallbackException("Unable to connect", err)

        # Convert JSON string to Dict
        if json_string:
            return json.loads(json_string)
        else:
            return None


class LocalStore(Store):
    def __init__(self):
        pass

    def set_dict(self, key, val):
        db = dbm.open("mydb", "c")
        # Convert Dict to JSON string
        json_val = json.dumps(val)
        db[key] = json_val
        db.close()

    def get_dict(self, key):
        try:
            db = dbm.open("mydb", "r")
            json_string = db.get(key)
            db.close()
            if json_string:
                return json.loads(json_string)
            else:
                return None
        except Exception as err:
            logging.error(f" Error reading from cache , {str(err)}")
            raise SystemError("Unable to connect", err)
