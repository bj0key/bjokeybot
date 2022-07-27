import asyncio

import discord
from discord.ext import commands

from bjokeybot import cogs, logger
from bjokeybot.constants import ACCESS_TOKEN
from bjokeybot.logger import log

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="bjokey, ", intents=intents)

bot.help_command = None

logger.init_logger()


async def setup():
    for cog in cogs.all_cogs:
        await bot.add_cog(cog())


def main():
    log.info(f"Starting bot...")
    bot.run(ACCESS_TOKEN)


if __name__ == "__main__":
    asyncio.run(setup())
    main()
