import random

from bjokeybot.constants import BJOKEY_IMAGE
from bjokeybot.logger import log
from discord.ext import commands


class FunCog(commands.Cog):
    @commands.command(name="bjokey")
    async def bjokey(self, ctx: commands.Context) -> None:
        "spits out a bjokey into chat"
        log.info("%s ran bjokey.", ctx.author.name)
        if random.random() < 0.94:
            await ctx.reply("bjokey")
        else:
            await ctx.reply("rare bjokey", file=BJOKEY_IMAGE)

    @commands.command(name="femham")
    async def femham(self, ctx: commands.Context) -> None:
        log.info("%s ran femham.", ctx.author.name)
        if ctx.message.author.id == 66183829148151808:
            await ctx.reply("Why are you trying to use the command, cris")
        else:
            await ctx.reply(f"stop femming cris{'tine'*random.randint(0,1)}")
