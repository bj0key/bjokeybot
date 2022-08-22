import asyncio

import discord
from discord.ext import commands

from bjokeybot import cogs, logger
from bjokeybot.constants import ACCESS_TOKEN
from bjokeybot.logger import log

logger.init_logger()


class BjokeyBot(commands.Bot):

    async def setup_hook(self) -> None:
        for cog in cogs.all_cogs:
            await self.add_cog(cog(self))


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = BjokeyBot(command_prefix="bjokey, ", intents=intents)

bot.help_command = None


def main():
    log.info("Starting bot...")
    bot.run(ACCESS_TOKEN)


if __name__ == "__main__":
    main()
