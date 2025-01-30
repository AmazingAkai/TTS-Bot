import os

import aiohttp
import arc
import hikari

from tts import plugin as tts

bot = hikari.RESTBot(
    token=os.environ["TOKEN"],
    public_key=os.environ["PUBLIC_KEY"],
    logs=os.environ["LOG_LEVEL"],
)
client = arc.RESTClient(
    bot,
    autosync=os.environ["AUTOSYNC"] == "true",
)

client.add_plugin(tts)


@client.add_startup_hook
async def startup_hook(client: arc.RESTClient) -> None:  # noqa: RUF029
    session = aiohttp.ClientSession()
    client.set_type_dependency(aiohttp.ClientSession, session)


@client.add_shutdown_hook
async def shutdown_hook(client: arc.RESTClient) -> None:
    session = client.get_type_dependency(aiohttp.ClientSession)
    await session.close()


if __name__ == "__main__":
    bot.run()
