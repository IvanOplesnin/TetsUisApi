import aiohttp

from add_number import add_number
from config import *


async def create_employee(
        first_name, last_name, phone_number, extension_phone_number, patronymic=None
        ):
    body = {
        "jsonrpc": "2.0",
        "id": "number",
        "method": "create.employees",
        "params": {
            "access_token": TOKEN,
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "status": "available",
            "in_external_allowed_call_directions": ["in", "out"],
            "in_internal_allowed_call_directions": ["in", "out"],
            "out_external_allowed_call_directions": ["in", "out"],
            "out_internal_allowed_call_directions": ["in", "out"],
            "phone_numbers": [
                {
                    "phone_number": phone_number,
                    "channels_count": 2,
                    "dial_time": 30,
                }
            ],
            "extension": {
                "extension_phone_number": extension_phone_number,
            }
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=BASE_URL, json=body, headers=HEADERS) as resp:
            response = await resp.json()
            return response

async def main():
    new_number = await add_number(TOKEN)
