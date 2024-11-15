import os
from os.path import join, dirname
from dotenv import load_dotenv
import logging

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STR = os.environ.get("SESSION_STR")
CHANNEL_IDS = os.environ.get("CHANNEL_IDS")
BOT_ID = os.environ.get("BOT_ID")
DEFAULT_AMOUNT = os.environ.get("DEFAULT_AMOUNT")
ADMIN_ID = os.environ.get("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)