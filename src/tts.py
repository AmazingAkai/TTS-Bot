import logging
import os

import arc
import hikari
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError
from hikari import files

DEEPGRAM_API_BASE_URL = "https://api.deepgram.com/v1"
DEEPGRAM_API_KEY = os.environ["DEEPGRAM_KEY"]

log = logging.getLogger("tts")
plugin = arc.RESTPlugin("tts")


@plugin.inject_dependencies
async def fetch_tts(text: str, session: ClientSession = arc.inject()) -> bytes:
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"text": text}

    async with session.post(
        DEEPGRAM_API_BASE_URL + "/speak",
        headers=headers,
        json=data,
    ) as response:
        log.debug("Response headers: %s", response.headers)

        response.raise_for_status()
        return await response.read()


@plugin.include
@arc.message_command(name="Read Aloud")
async def read_aloud(ctx: arc.RESTContext, message: hikari.Message) -> None:
    if not message.content:
        embed = hikari.Embed(
            title="Error (No Content)",
            description="Please provide some text to read aloud.",
            colour=hikari.Colour(0xED4245),
        )
        await ctx.respond(embed=embed)
        return

    tts = await fetch_tts(message.content)
    await ctx.respond(attachment=files.Bytes(tts, "tts.mp3"))


@read_aloud.set_error_handler
async def read_aloud_error_handler(ctx: arc.RESTContext, exception: Exception) -> None:
    if isinstance(exception, ClientResponseError):
        embed = hikari.Embed(
            title=f"Response Error (Status: {exception.status})",
            description=f"Error fetching audio from Deepgram: {exception.message}",
            colour=hikari.Colour(0xED4245),
        )
        await ctx.respond(embed=embed)
        return

    raise exception
