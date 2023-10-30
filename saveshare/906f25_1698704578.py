import aiohttp

class Http:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.nowpayments.io/v1/'
        self.timeout = 10  # 10 seconds
        self.headers = {
            'x-api-key': api_key,
        }
        self.session = aiohttp.ClientSession(
            headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        )

    async def get(self, url, params=None):
        async with self.session.get(self.base_url + url, params=params) as response:
            return await response.json()

    async def post(self, url, params=None):
        async with self.session.post(self.base_url + url, json=params) as response:
            return await response.json()

    async def close(self):
        await self.session.close()
