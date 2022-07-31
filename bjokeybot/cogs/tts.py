from base64 import b64decode
from io import BytesIO

import discord
from aiohttp import request
from bjokeybot.constants import DECTALK_URL, TIKTOK_URL
from bjokeybot.logger import log
from discord.ext import commands


class TTSCog(commands.Cog):
    @commands.command(name="tiktok")
    async def tiktok(self, ctx: commands.Context, *args: str) -> None:
        msg = " ".join(args)
        log.info('%s asked the tiktok TTS to say "%s"', ctx.author.name, msg)
        data = {
            "text_speaker": "en_us_001",
            "req_text": msg,
        }

        async with request("POST", TIKTOK_URL, data=data) as r:
            r_json = await r.json()
        audio = b64decode(r_json["data"]["v_str"])

        with BytesIO(audio) as f:
            await ctx.reply(file=discord.File(fp=f, filename="tts.mp3"))

    @commands.command(name="moonbase")
    async def moonbase(self, ctx: commands.Context, *args: str) -> None:
        msg = " ".join(args)
        log.info('%s asked the DECTalk TTS to say "%s"', ctx.author.name, msg)

        async with request("GET", DECTALK_URL, params={"text": msg}) as r:
            with BytesIO(await r.read()) as f:
                await ctx.reply(file=discord.File(fp=f, filename="tts.wav"))
