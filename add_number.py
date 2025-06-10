import asyncio
import json

import aiohttp

from main import base_url, header


def read_token(path="token.txt"):
    with open(path, "r") as f:
        token = f.read()
    return token


async def add_number(token=None):
    with open("numbers.json", "r") as f:
        data = json.load(f)

    number = data.get("result").get("data")[0].get("phone_number")
    print(number)
    body = {
        "jsonrpc": "2.0",
        "id": "number",
        "method": "enable.virtual_numbers",
        "params": {
            "access_token": token if token else read_token(),
            "virtual_phone_number": number
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=base_url,
                headers=header,
                json=body
        ) as response:
            print(await response.json())


async def delete_number(token=None):
    with open("numbers.json", "r") as f:
        data = json.load(f)
    number = data.get("result").get("data")[0].get("phone_number")
    print(number)

    async with aiohttp.ClientSession() as session:
        body = {
            "jsonrpc": "2.0",
            "id": "number",
            "method": "disable.virtual_numbers",
            "params": {
                "access_token": token if token else read_token(),
                "virtual_phone_number": number
            }
        }
        async with session.post(
                url=base_url,
                headers=header,
                json=body
        ) as resp:
            if resp.status == 200:
                print(await resp.json())


if __name__ == "__main__":
    asyncio.run(add_number())
