import asyncio
import json

import aiohttp

from add_number import read_token
from config import *


async def get_virtual_numbers():
    token = read_token()

    async with aiohttp.ClientSession() as session:
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.virtual_numbers",
            "params": {
                "access_token": token,
            }
        }
        async with session.post(
                url=BASE_URL,
                json=body,
                headers=HEADERS
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def main():
    result = await get_virtual_numbers()
    print(result)
    with open('virtual_numbers.json', 'w') as file:
        json.dump(result, file, indent=4)


if __name__ == '__main__':
    asyncio.run(main())
