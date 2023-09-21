import logging
import os

from dotenv import load_dotenv

dotenv_path = os.getenv("ENVIRONMENT_FILE")
logging.info(f"dotenv_path : {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)

APP_HOST = os.environ.get("HOST")
APP_PORT = os.environ.get("PORT")
APP_DEBUG = bool(os.environ.get("DEBUG"))
STORE_PATH = os.environ.get("STORE_PATH")

logging.info(f"App Host : {APP_HOST}")
logging.info(f"App Port : {APP_PORT}")
logging.info(f"App Debug : {APP_DEBUG}")
logging.info(f"Store Path : {STORE_PATH}")
