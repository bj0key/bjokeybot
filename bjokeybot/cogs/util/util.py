import ast
import re

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

ANSI_TAGS = {
    "fxnorm": 0,  # normal text
    "fxbold": 1,  # bold text
    "fxundr": 4,  # underlined text
    "gray": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "pink": 35,
    "cyan": 36,
    "white": 37,
    "bgdarkblue": 40,
    "bgorange": 41,
    "bgblue": 42,
    "bgturquoise": 43,
    "bggray": 44,
    "bgindigo": 45,
    "bglgray": 46,
    "bgwhite": 47
}

ANSI_PATTERN = re.compile(r"\$\[(\w+?)]")


def match_to_esc(match: re.Match[str]) -> str:
    return f"\x1b[{ANSI_TAGS[match.group(1)]}m"


class GeneralUtilityCog(BjokeyCog):

    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, username: str = None) -> None:
        """Gets and replies with the avatar of the user specified. Default to own avatar if not specified."""
        if not username:
            username = ctx.author.name
        log.info("%s asked for %s's avatar.", ctx.author.name, username)
        if ctx.guild is None:
            await ctx.reply("This only works in the server.")
            return
        user = ctx.guild.get_member_named(username)
        if user is None:
            await ctx.reply("⚠ Couldn't find user!")
        else:
            await ctx.reply(user.display_avatar.url)

    @commands.command(name="ansi")
    async def ansi(self, ctx: commands.Context, *, message: str) -> None:
        try:
            subbed_out = ANSI_PATTERN.sub(match_to_esc, message)
            await ctx.reply(f"```ansi\n{subbed_out}```")
        except KeyError as e:
            await ctx.reply(f"⚠ Uuh, I don't know what colour {e} is meant to be...")

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_tree(self, ctx: commands.Context) -> None:
        msg = await ctx.reply("Syncing...")
        await self.bot.tree.sync()
        await ctx.message.add_reaction("✅")
