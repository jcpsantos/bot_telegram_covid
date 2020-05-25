import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_API_URL = os.getenv("BASE_API_URL")
BASE_CSV_URL= os.getenv("BASE_CSV_URL")
BASE_GRAFICO_URL = os.getenv("BASE_GRAFICO_URL")
IMAGE_GRAFICO = os.getenv("IMAGE_GRAFICO")
IMG_DROPBOX = os.getenv("IMG_DROPBOX")