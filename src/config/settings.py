from config.config_manager import ConfigManager

APP_HOST = ConfigManager.getInstance().getConfig("HOST")
APP_PORT = ConfigManager.getInstance().getConfig("PORT")
APP_DEBUG = bool(ConfigManager.getInstance().getConfig("DEBUG"))
STORE_PATH = ConfigManager.getInstance().getConfig("STORE_PATH")
CACHE_TYPE = ConfigManager.getInstance().getConfig("CACHE_TYPE")
REDIS_HOST = ConfigManager.getInstance().getConfig("REDIS_HOST")
REDIS_PORT = ConfigManager.getInstance().getConfig("REDIS_PORT")
REDIS_PWD = ConfigManager.getInstance().getConfig("REDIS_PWD")
