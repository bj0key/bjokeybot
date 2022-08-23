from datetime import datetime

from discord.ext import commands

from bjokeybot.cogs import all_cogs


class BjokeyBot(commands.Bot):
    async def setup_hook(self) -> None:
        for cog in all_cogs:
            await self.add_cog(cog(self))
