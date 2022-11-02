import discord
from discord.ext import commands

from bjokeybot.cogs import all_cogs


class BjokeyBot(commands.Bot):
    async def setup_hook(self) -> None:
        for cog in all_cogs:
            await self.add_cog(cog(self))

    async def on_ready(self):
        await self.change_presence(activity=discord.Streaming(name="Fornite, and drinking cola?", url="https://www.twitch.tv/crool_"))
