from base64 import b64decode
from io import BytesIO

import discord
from aiohttp import request
from bjokeybot.constants import TIKTOK_URL
from bjokeybot.logger import log
from discord.ext import commands


class TTSCog(commands.Cog):
    @commands.command(name="tiktok")
    async def tiktok(self, ctx: commands.Context) -> None:
        msg = ctx.message.content.removeprefix("bjokey, tiktok")
        log.info('%s asked tiktok to say "%s"', ctx.author.name, msg)
        data = {
            "text_speaker": "en_us_001",
            "req_text": ctx.message.content.removeprefix("bjokey, tiktok"),
        }

        async with request("POST", TIKTOK_URL, data=data) as r:
            r_json = await r.json()
        audio = b64decode(r_json["data"]["v_str"])

        with BytesIO(audio) as f:
            await ctx.reply(file=discord.File(fp=f, filename="tts.mp3"))
