from datetime import datetime

from discord.ext import commands

from bjokeybot import cogs


class BjokeyBot(commands.Bot):
    def __init__(self):
        self.start_time = datetime.now()
        """The time of initialisation, AKA when the bot was started"""

    async def setup_hook(self) -> None:
        for cog in cogs.all_cogs:
            await self.add_cog(cog(self))
