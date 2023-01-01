import asyncio
import requests
from typing import List, Dict

import aiohttp


async def get_url(session: aiohttp.ClientSession, url: str) -> Dict:
    async with session.get(url) as response:
        return await response.json()


async def request_multiple_urls(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks: List[asyncio.Task] = []
        for url in urls:
            tasks.append(
                asyncio.ensure_future(
                    get_url(session, url)
                )
            )
        return await asyncio.gather(*tasks)


async def get_request_url(url: str, params: dict = {}):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def get_data(url: str, params: dict = {}):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(response.json())
        print("sucessfully fetched the data")

        return response
    else:
        print(f"Hello person, there's a {response.status_code} error with your request")
        return