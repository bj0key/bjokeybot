import random
from io import BytesIO

from bjokeybot.logger import log
from discord import File
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
        if ctx.message.author.id == 66183829148151808:
            await ctx.reply("Why are you trying to use the command, cris")
        else:
            await ctx.reply(f"stop femming cris{'tine' * random.randint(0, 1)}")

    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, username: str) -> None:
        if username == "":
            username = ctx.author.name
        log.info("%s asked for %s's avatar.", ctx.author.name, username)
        user = ctx.guild.get_member_named(username)
        if user is None:
            await ctx.reply("⚠ Couldn't find user!")
        else:
            await ctx.reply(user.display_avatar.url)
