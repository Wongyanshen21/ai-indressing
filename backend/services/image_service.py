import httpx


async def download_image(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.content
