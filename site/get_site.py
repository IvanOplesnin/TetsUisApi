import json

import aiohttp

from config import *
from add_number import read_token

async def get_site():
    body = {
        "jsonrpc": "2.0",
        "id": "number",
        "method": "get.sites",
        "params": {
            "access_token": TOKEN,
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=BASE_URL,
                headers=HEADERS,
                json=body
        ) as response:
            print(response)
            return await response.json()


async def main():
    site = await get_site()
    print(site)
    if not site.get("error"):
        sites = site.get("result").get("data")
        with open("sites.json", "w") as file:
            json.dump(sites, file, indent=4)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
