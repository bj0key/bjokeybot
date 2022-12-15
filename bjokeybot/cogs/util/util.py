import ast

from discord.ext import commands

from bjokeybot.cogs.base import BjokeyCog
from bjokeybot.logger import log

EVAL_WHITELIST = (
    ast.Expression,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.BinOp,
    ast.UnaryOp,
    ast.operator,
    ast.unaryop,
    ast.cmpop,
    ast.Num,
)


class GeneralUtilityCog(BjokeyCog):

    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, username: str = None) -> None:
        """Gets and replies with the avatar of the user specified. Default to own avatar if not specified."""
        if not username:
            username = ctx.author.name
        log.info("%s asked for %s's avatar.", ctx.author.name, username)
        user = ctx.guild.get_member_named(username)
        if user is None:
            await ctx.reply("⚠ Couldn't find user!")
        else:
            await ctx.reply(user.display_avatar.url)
