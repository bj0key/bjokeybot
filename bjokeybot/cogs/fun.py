import random
from io import BytesIO

from bjokeybot.logger import log
from discord import File, DiscordException
from discord.ext import commands

with open("resources/bjokey.png", "rb") as f:
    bjokey_image = BytesIO(f.read())


class FunCog(commands.Cog):
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
        hammed = False
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
