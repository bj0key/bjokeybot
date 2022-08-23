from base64 import b64decode
from io import BytesIO

import discord
from aiohttp import request
from discord.ext import commands

from bjokeybot.bot import BjokeyBot
from bjokeybot.constants import DECTALK_URL, TIKTOK_URL
from bjokeybot.logger import log


async def get_tiktok(msg) -> bytes:
    """Use the tiktok API to get a text-to-speech MP3
    Returns a bytes object containing the file data."""
    data = {
        "text_speaker": "en_us_001",
        "req_text": msg,
    }
    async with request("POST", TIKTOK_URL, data=data) as r:
        r_json = await r.json()
    try:
        audio = b64decode(r_json["data"]["v_str"])
    except KeyError as e:
        log.error("Couldn't fetch audio! got %s instead.", r_json)
        return b""
    return audio


async def get_moonbase(msg) -> bytes:
    async with request("GET", DECTALK_URL, params={"text": msg}) as r:
        return await r.read()


class TTSCog(commands.Cog):
    def __init__(self, bot: BjokeyBot) -> None:
        self.bot = bot

    @commands.command(name="tiktok")
    async def tiktok(self, ctx: commands.Context, *args: str) -> None:
        msg = " ".join(args)
        log.info('%s asked the tiktok TTS to say "%s"', ctx.author.name, msg)

        audio = await get_tiktok(msg)
        if len(audio) == 0:
            await ctx.reply("Command failed! Maybe the TTS service is down? "
                            "Did you put any naughty words in your message?")
            return

        with BytesIO(audio) as f:
            await ctx.reply(file=discord.File(fp=f, filename="tts.mp3"))

    @commands.command(name="moonbase")
    async def moonbase(self, ctx: commands.Context, *args: str) -> None:
        msg = " ".join(args)
        log.info('%s asked the DECTalk TTS to say "%s"', ctx.author.name, msg)

        audio = await get_moonbase(msg)
        if len(audio) == 0:
            await ctx.reply("Command failed! Maybe the TTS service is down? "
                            "Did you put any naughty words in your message?")
            return

        with BytesIO(audio) as f:
            await ctx.reply(file=discord.File(fp=f, filename="tts.wav"))
