import asyncio
import json

import aiohttp

from add_number import read_token
from config import *


async def get_employees():
    token = read_token(r"C:\Users\aples\PycharmProjects\TestDataApi\token.txt")
    body = {
        "jsonrpc": "2.0",
        "id": "number",
        "method": "get.employees",
        "params": {
            "access_token": TOKEN
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=BASE_URL, json=body, headers=HEADERS) as response:
            if response.status == 200:
                response = await response.json()
                with open('employees.json', 'w') as file:
                    json.dump(response, file, indent=4)
                print('Success')
            else:
                print('Error')


if __name__ == '__main__':
    asyncio.run(get_employees())

