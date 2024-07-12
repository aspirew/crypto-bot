import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STR = os.environ.get("SESSION_STR")
CHANNEL_IDS = os.environ.get("CHANNEL_IDS")