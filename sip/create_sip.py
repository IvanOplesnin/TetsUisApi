import json

import aiohttp

from add_number import read_token
from config import *
from get_virtual_numbers import get_virtual_numbers


async def create_sip(employee_id: int, virtual_phone_number: str) -> dict:
    token = read_token()
    body = {
        "jsonrpc": "2.0",
        "id": "number",
        "method": "create.sip_lines",
        "params": {
            "access_token": token,
            "employee_id": employee_id,
            "virtual_phone_number": virtual_phone_number
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=BASE_URL,
                json=body,
                headers=HEADERS
        ) as resp:
            response = await resp.json()
            return response['id']


async def main():
    numbers = await get_virtual_numbers()
    number = [number for number in numbers if not number['scenarios']][-1]
    with open(r'C:\Users\aples\PycharmProjects\TestDataApi\employee\employees.json', 'r') as file:
        data = json.load(file)
        employee_id = data.get("result").get("data")[0].get("id")
