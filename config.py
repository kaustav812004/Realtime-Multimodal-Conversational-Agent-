# config.py
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-06-01-preview")

CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_API_VERSION = os.getenv("CAL_API_VERSION", "2024-06-14")
CAL_BASE = "https://api.cal.com"