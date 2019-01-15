import aiohttp
import asyncio


async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://0.0.0.0:8080/') as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        print(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

loop = asyncio.get_event_loop()
loop.run_until_complete(fetch())
