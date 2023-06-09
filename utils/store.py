import json, dbm
import redis
from utils.config import Config
from utils.exceptions import HaltCallbackException
from abc import ABC, abstractmethod

class Store_Factory:
    def get_store():
        config = Config()
        cache_type = config.get("CACHE", "CACHE_TYPE", fallback="local")
        if cache_type == "local":
            return LocalStore()
        else:
            return RedisStore()
        

class Store(ABC):
    @abstractmethod
    def set_dict(self, key, val):
        pass

    def get_dict (self, key):
        pass

class RedisStore(Store):
    def __init__(self):
        config = Config()
        host=config.get("REDIS", "HOST", fallback="localhost")
        port=config.get("REDIS", "PORT", fallback=6379)
        password=config.get("REDIS", "PWD", fallback="")
        self.client = redis.StrictRedis(
            host, port, password, decode_responses=True,
        )

    def set_dict(self, key, val):
        # Convert Dict to JSON string
        json_val = json.dumps(val)
        try:
            self.client.set(key, json_val)
        except redis.exceptions.ConnectionError as err:
            raise HaltCallbackException("Unable to connect", err)

    def get_dict (self, key):
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
        db = dbm.open('mydb','c')
        # Convert Dict to JSON string
        json_val = json.dumps(val)
        db[key] = json_val
        db.close()
        

    def get_dict (self, key):
        db = dbm.open('mydb','c')
        json_string = db.get(key)
        db.close()
        # Convert JSON string to Dict
        if json_string:
            return json.loads(json_string)
        else:
            return None

