import os

import dotenv

BASE_URL = "https://dataapi.uiscom.ru/v2.0"
CALL_URL = "https://callapi.uiscom.ru/v4.0"
HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
}
dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
