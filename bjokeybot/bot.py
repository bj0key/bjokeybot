from discord.ext import commands

from bjokeybot import cogs


class BjokeyBot(commands.Bot):

    async def setup_hook(self) -> None:
        for cog in cogs.all_cogs:
            await self.add_cog(cog(self))
