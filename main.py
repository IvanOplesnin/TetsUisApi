import asyncio
import json

import aiohttp as a

from config import TOKEN

base_url = "https://dataapi.uiscom.ru/v2.0"

header = {
    "Content-Type": "application/json; charset=utf-8",
}


def create_filter(field, operator, value):
    return {
        "field": field,
        "operator": operator,
        "value": value
    }


async def authorization(login, password):
    async with a.ClientSession() as session:
        body = {
            "jsonrpc": "2.0",
            "id": "req1",
            "method": "login.user",
            "params": {
                "login": login,
                "password": password
            }
        }
        result = await session.post(
            url=base_url,
            headers=header,
            json=body
        )

        return result


async def get_account(token):
    async with a.ClientSession() as session:
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.account",
            "params": {
                "access_token": token
            }
        }

        result = await session.post(
            url=base_url,
            headers=header,
            json=body
        )
        return result


async def get_numbers(token):
    async with a.ClientSession() as session:
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "get.available_virtual_numbers",
            "params": {
                "access_token": token,
                "limit": 10,
                "filter": {
                    "filters": [
                        create_filter("location_mnemonic", "=", "msk"),
                        create_filter("category", "=", "usual")
                    ],
                    "condition": "and"
                }
            }
        }
        async with session.post(
            url=base_url,
            headers=header,
            json=body
        ) as result:
            if result.status == 200:
                return await result.json()


async def main():
    numbers = await get_numbers(TOKEN)
    print(numbers)
    with open("numbers.json", "w") as file:
        json.dump(numbers, file, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
