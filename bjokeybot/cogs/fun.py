import asyncio
import random
from io import BytesIO
from urllib.parse import urlparse

from discord import File, DiscordException
from discord.ext import commands

from bjokeybot.bot import BjokeyBot
from bjokeybot.constants import SCRAN_CHANNEL
from bjokeybot.logger import log

with open("resources/bjokey.png", "rb") as f:
    bjokey_image = BytesIO(f.read())


class FunCog(commands.Cog):
    def __init__(self, bot: BjokeyBot) -> None:
        self.bot = bot

    @commands.command(name="bjokey")
    async def bjokey(self, ctx: commands.Context) -> None:
        """spits out a bjokey into chat"""
        log.info("%s ran bjokey.", ctx.author.name)
        if random.random() < 0.94:
            await ctx.reply("bjokey")
        else:
            await ctx.reply(
                "rare bjokey", file=File(bjokey_image, filename="bjokey.png")
            )
            bjokey_image.seek(0)

    @commands.command(name="femham")
    async def femham(self, ctx: commands.Context) -> None:
        log.info("%s ran femham.", ctx.author.name)
        if ctx.message.author.id == 66183829148151808:
            await ctx.reply("Why are you trying to use the command, cris")
            hammed = True
        else:
            hammed = random.randint(0, 1)
            await ctx.reply(f"stop femming cris{'tine' * hammed}")

        if hammed:
            try:
                await ctx.author.edit(nick="femhammer " + (ctx.author.nick or ctx.author.name))
            except DiscordException as e:
                log.warn("Femham renaming raised exception %s: %s", e.__class__.__name__, str(e).replace("\n", " "))

    @commands.command(name="target")
    async def target(self, ctx: commands.Context, *, t: str) -> None:
        """Drone strike a target"""
        log.info("%s targeted %s.", ctx.author.name, t)
        if t.lower() == "israel":
            await ctx.reply("https://cdn.discordapp.com/attachments/364933355290099714/1009473800217317407/unknown.png")
        else:
            async with ctx.typing():
                msg = await ctx.reply(f"Targeting {t}...")
                await asyncio.sleep(2)
                await msg.edit(
                    content="https://cdn.discordapp.com/attachments/364933355290099714/1009474594387795980/unknown.png")
                await asyncio.sleep(2)
                await msg.edit(content=f"{t} successfully eliminated")

    @commands.command(name="scran")
    async def get_scran(self, ctx: commands.Context) -> None:
        """Get a random bit of scran from the scran channel"""
        # Note: while pulling data live from the channel is cool,
        # instead reading from a cached list would probably be wiser
        for channel in ctx.guild.text_channels:
            if channel.id == SCRAN_CHANNEL:
                scran_channel = channel
                break
        else:
            log.error("Couldn't find scran channel!")
            await ctx.reply("⚠ we all outta scran")
            return

        scran = []
        async for msg in scran_channel.history(limit=400):
            if len(msg.attachments) > 0:
                scran += msg.attachments

            else:
                # Check to see if message contains a valid URL
                if urlparse(msg.content).netloc != "":
                    scran.append(msg.content)

        await ctx.reply(random.choice(scran))
