import logging
import os

import arc
import hikari
from aiohttp import ClientSession
from hikari import files

from exception import TTSError

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
        if response.status != 200:
            raise TTSError(
                title=f"Response Error (Status: {response.status})",
                message=f"Failed to respond with message: {response.reason}",
            )
        return await response.read()


@plugin.include
@arc.message_command(name="Read Aloud", autodefer=True)
async def read_aloud(ctx: arc.RESTContext, message: hikari.Message) -> None:
    if not message.content:
        raise TTSError(
            title="Error (No Content)",
            message="Please provide some text to read aloud.",
        )
    if len(message.content) > 2000:
        raise TTSError(
            title="Error (Too Long)",
            message="Please provide a shorter message to read aloud.",
        )

    tts = await fetch_tts(message.content)
    await ctx.respond(attachment=files.Bytes(tts, "tts.mp3"))


@read_aloud.set_error_handler
async def read_aloud_error_handler(ctx: arc.RESTContext, exception: Exception) -> None:
    if isinstance(exception, TTSError):
        embed = hikari.Embed(
            title=exception.title,
            description=exception.message,
            colour=hikari.Colour(0xED4245),
        )
        await ctx.respond(embed=embed)
        return

    raise exception
