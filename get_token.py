import asyncio
import os

import aiohttp as a
from config import *


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
            url=BASE_URL,
            headers=HEADERS,
            json=body
        )
        print(result)
        if result.status == 200:
            data = await result.json()
            print(data)

            token = data.get("result").get("data").get("access_token")
            with open("token.txt", "w") as file:
                file.write(token)

        return result


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv("PASSWORD")
    asyncio.run(authorization(LOGIN, PASSWORD))
